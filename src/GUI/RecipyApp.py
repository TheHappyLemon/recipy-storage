import tkinter as tk
from src.system.config import Config
from src.system.InvertedIndex import InvertedIndex
from src.system.InvertedIndex import BaseIndex
from src.exceptions.KeywordsNotFound import KeywordsNotFoundError
import os
import json
from src.recipies.recipy import Recipy

class RecipyApp(tk.Tk):

    def __init__(self):
        super().__init__()
        # Initialize inverted index
        self.config = Config()
        self.index = self.build_index()
        self.index.sort_index()
        keywords = sorted(self.index.get_terms())
        self.title("Recipy Finder")

        # Create Include and Exclude Listboxes using helper method
        self.include_listbox = self._create_keyword_listbox("INCLUDE keywords", keywords)
        self.exclude_listbox = self._create_keyword_listbox("EXCLUDE keywords", keywords)

        # Button row (Search + Clear Selections)
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Search", command=self.search).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear Selections", command=self.clear_selections).pack(side=tk.LEFT, padx=5)

        # Results label
        self.results = tk.Text(self, height=10)
        self.results.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def build_index(self) -> InvertedIndex:
        if self.config.cache != None:
            try:
                index = InvertedIndex(",")
                with open(self.config.cache, 'r', encoding='utf-8') as f:
                    index.index = json.load(f)
                index.print("InvertedIndex_fromcache.json", index.index)
                return index
            # In case of exception I want to continue, so it
            # would initialize index from scratch
            except FileNotFoundError:
                print(f"Cache file {self.config.cache} not found! Building index from scratch")
            except Exception as e:
                print(f"Failed loading cache: {str(e)}! Building index from scratch")
            
        documents = {}
        for filename in os.listdir(self.config.recipy_directory):
            if not filename.endswith('.txt'):
                continue

            filepath = os.path.join(self.config.recipy_directory, filename)
            try:
                recipy = Recipy()
                recipy.load(filepath)
                documents[filename] = recipy.get_keywords_raw()
            except FileNotFoundError:
                continue
            except KeywordsNotFoundError:
                print(f"File {filepath}: does not have any keywords!")
                continue
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
                continue
        index = InvertedIndex(",")
        for doc in documents:
            tokens = index.tokenize(document=documents[doc])
            index.update_index(tokens, doc)
        index.print("InvertedIndex.json", index.index)
        return index

    def _create_keyword_listbox(self, label_text : str, keywords : list):
        """Create a labeled Listbox with scrollbar and populate it with keywords."""
        tk.Label(self, text=label_text).pack()
        frame = tk.Frame(self)
        frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        listbox = tk.Listbox(
            frame, selectmode=tk.MULTIPLE, exportselection=False, height=10, yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=listbox.yview)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for kw in keywords:
            listbox.insert(tk.END, kw)

        return listbox

    def search(self):
        include = [self.include_listbox.get(i) for i in self.include_listbox.curselection()]
        exclude = [self.exclude_listbox.get(i) for i in self.exclude_listbox.curselection()]
        
        self.results.delete("1.0", tk.END)
        if include == [] and exclude == []:
            self.results.insert(tk.END, f"No keywords choosen!")
            return
        self.results.insert(
            tk.END,
            f"Searching for recipies!\nIncluding: {", ".join(include).strip()}\n" +
            f"Excluding: {", ".join(exclude).strip()}\n\n"
        )
        
        if include == []:
            # If we want to only exclude:
            # 1. Take all files
            # 2. Take all files that contain ANY of exclusion terms
            # 3. Substract point 2 result from point 1 result 
            all_files = set(self.index.get_postings())
            exclusion_files = set()
            for term in exclude:
                filenames = set(self.index.get_postings(term))
                exclusion_files.update(filenames)
            querry_result = all_files.difference(exclusion_files)
        elif exclude == []:
            # If we want to only include:
            # Return files that ALL HAVE provided terms
            querry_result = self.index.QuerryAnd(include)
        else:
            # If we want to exclude something and include something
            # 1. Get all files that ALL have INCLUSION terms
            # 2. Get all files that HAVE ANY EXCLUSION term
            # 3. Substract point 2 result from point 1 result 
            inclusion_files = set(self.index.QuerryAnd(include))
            exclusion_files = set()
            for term in exclude:
                filenames = set(self.index.get_postings(term))
                exclusion_files.update(filenames)
            querry_result = inclusion_files.difference(exclusion_files)

        msg = "Search results:\n"
        if len(querry_result) == 0:
            msg = msg + "No recipies match :("
        else:
            msg = msg + ", ".join(querry_result).strip()
        self.results.insert(tk.END, msg)

    def clear_selections(self):
        self.include_listbox.selection_clear(0, tk.END)
        self.exclude_listbox.selection_clear(0, tk.END)

        
