import sys
from os import path
from bisect import bisect_right,insort_right

ORDER = 3

class BPlusTree(object) :

	#INITIALISE THE TREE BY CREATING A ROOT NODE
	def __init__(self) :
		self.root = BPlusTreeNode()
		self.all_keys_count = {}   #keeps track of number of occurrences of a key


	#INSERT A NEW KEY VALUE IN THE TREE
	def insert(self,key) :

		#If a key already exists, just increase its count, don't insert it
		if(key in self.all_keys_count) : 
			#print("inside already", key)
			self.all_keys_count[key] += 1

		else :
			self.all_keys_count[key] = 1 
			mid_val, new_node = self.insert_helper(key, self.root)
			
			#check if root needs a split 
			if mid_val :
				new_root = BPlusTreeNode()
				new_root.keys = [mid_val]
				new_root.pointers = [self.root, new_node]
				new_root.is_leaf = False
				self.root = new_root
	

	#HELPER FUNCTION FOR INSERTING A NEW KEY 
	def insert_helper(self,key,node) :

		'''If node is leaf
			1. Insert the key at its correct position
			2. If order exceeds, split the leaf
		'''
		if node.is_leaf:
			insort_right(node.keys, key)
			if len(node.keys) > ORDER:
				return node.split()
			return None, None

		#If node is not a leaf, recursively find the appropriate leaf 
		mid_val, new_node = self.insert_helper(key, node.pointers[bisect_right(node.keys, key)])

		if mid_val:

			#insert key at its place
			location = bisect_right(node.keys, mid_val)
			node.keys.insert(location, mid_val)
			node.pointers.insert(location + 1, new_node)

			#check if split is required
			if len(node.keys) > ORDER:
				return node.split()
			return None, None
		return None, None

		


	def get_leftmost_leaf(self,search_key, node) :

		#If the node is leaf,return
		if(node.is_leaf):
			return node

		#Else, find the leaf recusrively
		for i in range(len(node.keys)):

			#If search key is less than node's first key, go to the left child of current node
			if(i == 0  and search_key <= node.keys[i] ):
				return self.get_leftmost_leaf(search_key,node.pointers[0])

			#If search key is greater than the last key of current node, go to the right child of current node
			elif((search_key > node.keys[i]) and i+1==len(node.keys)):
				return self.get_leftmost_leaf(search_key,node.pointers[i+1])


			# If search key lies between smallest and largest key values of current node 
			elif(search_key <= node.keys[i+1] and node.keys[i] <= search_key ):
				return self.get_leftmost_leaf(search_key,node.pointers[i+1])


	#COUNT NO OF KEY IN A RANGE - 
	def count_keys_in_range(self,min_key,max_key) :
		#get the left most leaf that has key >= min_key
		node = self.get_leftmost_leaf(min_key, self.root)
		count = 0
		#traverse every leaf until there is no leaf left or the key > max_key
		while node:
			#print("inside while")

			for i in range(len(node.keys)) :
				if(node.keys[i] > max_key) :
					break
				if(node.keys[i] <= max_key and node.keys[i] >= min_key) :
					count += self.all_keys_count[node.keys[i]]
			node = node.next
		return count
		'''count = 0
		for i in self.all_keys_count :
			if(i >= min_key and i <= max_key) :
				count += self.all_keys_count[i]
		return count'''


	#FIND IF A KEY EXISTS -
	def find_key(self,key) :
		if(key in self.all_keys_count) :
			return True
		return False


	#COUNT THE NUMBER OF OCCURRENCES OF A KEY IN THE TREE - 
	def count_occurrences_of_key(self,key) :
		if(key in self.all_keys_count) :
			return self.all_keys_count[key]
		return 0





class BPlusTreeNode :

	#INITIALISE THE NODE
	def __init__(self) :
		self.pointers = []
		self.is_leaf = True
		self.next = None
		self.keys = []


	#SPLIT THE NODE 
	def split(self) :

		#create a new node 
		splitted_node = BPlusTreeNode()

		#find the mid position
		mid_position = len(self.keys) // 2
		mid_val = self.keys[mid_position]
	
		
		#If the node is a leaf
		if self.is_leaf :
			insertion_position = mid_position

		#If the node to be splitted is an internal node
		else :
			insertion_position = mid_position + 1
			
		#distribute key valeus to the new node and current node
		splitted_node.keys = self.keys[insertion_position : ]
		splitted_node.pointers = self.pointers[insertion_position : ]

		self.keys = self.keys[ : mid_position]
		self.pointers = self.pointers[:insertion_position]

		#point current node to the next node
		splitted_node.next = self.next
		self.next = splitted_node

		#update is_leaf 
		splitted_node.is_leaf = self.is_leaf
	

		#return the key  over which split occured and the new node formed after split
		return mid_val,splitted_node



#CHECK IF A QUERY IS IN VALID FORMAT -
def check_if_valid(query_parts) :

	length = len(query_parts)
	command = query_parts[0].lower()

	if(length > 1) : 
		if(command == "range" and length == 3) :
			return True
		if((command == "insert" or command == "find" or command == "count") and length == 2) :
			return True
	return False


#PROCESS QUERIES - 
def processQueries(queries) :
	flag = True
	with open("output.txt",'w') as out_file : 
		b_plus_tree = BPlusTree()

		for i in queries :

			query_parts = i.strip().split()

			#check if the query is valid - 
			if(check_if_valid(query_parts)) :
				command = query_parts[0].lower() 
				element = int(query_parts[1])

				if(command == "insert") :
					b_plus_tree.insert(element)
					result = str(element) + " inserted"

				elif(command == "find") :
					if(b_plus_tree.find_key(element)) :
						result = "YES"
					else :
						result = "NO"

				elif(command == "count") :
					result = str(b_plus_tree.count_occurrences_of_key(element)) 

				elif(command == "range") :
					result = str(b_plus_tree.count_keys_in_range(element,int(query_parts[-1])))

			else :
				result = "Invalid query"

			#write the result og the query to the output file
			out_file.write(result + "\n") 




#MAIN FUNCTION - 
def main() :

	#check if input file is provided : 
	if(len(sys.argv) < 2) :
		print("Provide the input file name")
		sys.exit(0)

	input_file = sys.argv[1]

	#check if file exits : 
	if(path.exists(input_file)) :
		with open(input_file,'r') as inp :
			queries = inp.readlines()
		processQueries(queries)
	else :
		print("File doesn't exist")
		sys.exit(0)



if __name__ == "__main__" :
	main()

