"""
Channel for pyppl
"""
import sys

from os import path
from glob import glob
from six import string_types
from . import utils

class Channel (list):
	"""
	The channen class, extended from `list`
	"""

	@staticmethod
	def create(l = None):
		"""
		Create a Channel from a list
		@params:
			`l`: The list, default: []
		@returns:
			The Channel created from the list
		"""
		if l is None: l = []
		if not isinstance(l, list): l = [l]
		ret = Channel()
		for e in l:
			ret.append (Channel._tuplize(e))
		return ret

	@staticmethod
	def fromChannels(*args):
		"""
		Create a Channel from Channels
		@params:
			`args`: The Channels
		@returns:
			The Channel merged from other Channels
		"""
		ret = Channel.create()
		return ret.insert (None, *args)
	
	@staticmethod
	def fromPattern(pattern, t = 'any', sortby = 'name', reverse=False):
		"""
		Create a Channel from a path pattern
		@params:
			`pattern`: the pattern with wild cards
			`t`:       the type of the files/dirs to include
			  - 'dir', 'file', 'link' or 'any' (default)
			`sortby`:  how the list is sorted
			  - 'name' (default), 'mtime', 'size'
			`reverse`: reverse sort. Default: False
		@returns:
			The Channel created from the path
		"""
		if sortby == 'name':
			key = str
		elif sortby == 'mtime':
			key = path.getmtime
		elif sortby == 'size':
			key = path.getsize
		ret = Channel.create(sorted(glob(pattern), key=key, reverse=reverse))
		if t == 'link':
			return ret.filterCol (func = path.islink)
		elif t == 'dir':
			return ret.filterCol (func = path.isdir)
		elif t == 'file':
			return ret.filterCol (func = path.isfile)
		return ret

	@staticmethod
	def fromPairs(pattern):
		"""
		Create a width = 2 Channel from a pattern
		@params:
			`pattern`: the pattern
		@returns:
			The Channel create from every 2 files match the pattern
		"""
		ret = sorted(glob(pattern))
		c = Channel.create()
		for i in range(0, len(ret), 2):
			c.append ((ret[i], ret[i+1]))
		return c
	
	@staticmethod
	def fromFile(fn, skip = 0, delimit = "\t"):
		"""
		Create Channel from the file content
		It's like a matrix file, each row is a row for a Channel.
		And each column is a column for a Channel.
		@params:
			`fn`:      the file
			`skip`:    first lines to skip
			`delimit`: the delimit for columns
		@returns:
			A Channel created from the file
		"""
		ret = Channel.create()
		with open(fn) as f:
			i = -1
			for line in f:
				i += 1
				if i < skip: continue
				line = line.strip()
				if not line: continue
				ret.append (tuple(line.split(delimit)))
		return ret

	@staticmethod
	def fromArgv():
		"""
		Create a Channel from `sys.argv[1:]`
		"python test.py a b c" creates a width=1 Channel
		"python test.py a,1 b,2 c,3" creates a width=2 Channel
		@returns:
			The Channel created from the command line arguments
		"""
		ret  = Channel.create()
		args = sys.argv[1:]
		alen = len (args)
		if alen == 0: return ret
		
		width = None
		for arg in args:
			items = tuple(utils.split(arg, ','))
			if width is not None and width != len(items):
				raise ValueError('Width %s (%s) is not consistent with previous %s' % (len(items), arg, width))
			width = len(items)
			ret.append (items)
		return ret
		
	@staticmethod
	def fromParams(*pnames):
		"""
		Create a Channel from params
		@params:
			`*pnames`: The names of the option
		@returns:
			The Channel
		"""
		from .parameters import params
		ret = Channel.create()
		width = None
		for pname in pnames:
			param = getattr(params, pname)
			data = param.value
			if param.type != list:
				data = [param.value]
			if width is not None and width != len(data):
				raise ValueError('Width %s (%s) is not consistent with previous %s' % (len(data), data, width))
			width = len(data)
			ret = ret.cbind(data)
		return ret
	
	@staticmethod
	def _tuplize(tu):
		"""
		A private method, try to convert an element to tuple
		If it's a string, convert it to `(tu, )`
		Else if it is iterable, convert it to `tuple(tu)`
		Otherwise, convert it to `(tu, )`
		Notice that string is also iterable.
		@params:
			`tu`: the element to be converted
		@returns:
			The converted element
		"""
		if isinstance(tu, string_types):
			tu = (tu, )
		else:
			try:
				iter(tu)
			except Exception:
				tu = (tu, )
		return (tu, ) if isinstance(tu, list) else tuple (tu)
		
	
	def expand(self, col = 0, pattern = "*", t = 'any', sortby = 'name', reverse=False):
		"""
		expand the Channel according to the files in <col>, other cols will keep the same
		`[(dir1/dir2, 1)].expand (0, "*")` will expand to
		`[(dir1/dir2/file1, 1), (dir1/dir2/file2, 1), ...]`
		length: 1 -> N
		width:  M -> M
		@params:
			`col`:     the index of the column used to expand
			`pattern`: use a pattern to filter the files/dirs, default: `*`
			`t`:       the type of the files/dirs to include
			  - 'dir', 'file', 'link' or 'any' (default)
			`sortby`:  how the list is sorted
			  - 'name' (default), 'mtime', 'size'
			`reverse`: reverse sort. Default: False
		@returns:
			The expanded Channel
		"""
		if len(self) == 0:
			raise ValueError('Cannot expand an empty Channel.')
			
		folder = self[0][col]
		
		ret = Channel.fromPattern(path.join(folder, pattern), t=t, sortby=sortby, reverse=reverse)
		
		if not ret:
			return Channel.create([self[0]])
		
		return ret.insert(0, *self[0][:col]).cbind(*self[0][(col+1):])
		
	def collapse(self, col = 0):
		"""
		Do the reverse of expand
		length: N -> 1
		width:  M -> M
		@params:
			`col`:     the index of the column used to collapse
		@returns:
			The collapsed Channel
		"""
		if len(self) == 0:
			raise ValueError('Cannot collapse an empty Channel.')
			
		paths = self.colAt(col).flatten()
		compx = path.dirname(path.commonprefix(paths))
		row   = list(self[0])
		row[col] = compx
		return Channel.create(tuple(row))
	
	def copy(self):
		"""
		Copy a Channel using `copy.copy`
		@returns:
			The copied Channel
		"""
		return self.slice(0)

	def width(self):
		"""
		Get the width of a Channel
		@returns:
			The width of the Channel
		"""
		if not self: return 0
		return len(self[0]) if isinstance(self[0], tuple) else 1
	
	def length(self):
		"""
		Get the length of a Channel
		It's just an alias of `len(chan)`
		@returns:
			The length of the Channel
		"""
		return len(self)

	def map (self, func):
		"""
		Alias of python builtin `map`
		@params:
			`func`: the function
		@returns:
			The transformed Channel
		"""
		return Channel.create(utils.map(func, self))
		
	def mapCol(self, func, col = 0):
		"""
		Map for a column
		@params:
			`func`: the function
			`col`: the index of the column. Default: 0
		@returns:
			The transformed Channel
		"""
		return Channel.create([
			s[:col] + (func(s[col]), ) + s[(col+1):] for s in self
		])

	def filter (self, func = None):
		"""
		Alias of python builtin `filter`
		@params:
			`func`: the function. Default: None
		@returns:
			The filtered Channel
		"""
		return Channel.create(utils.filter(func, self))
	
	def filterCol(self, func = None, col = 0):
		"""
		Just filter on the first column
		@params:
			`func`: the function
			`col`: the column to filter
		@returns:
			The filtered Channel
		"""
		if func is None: func = bool
		return Channel.create([s for s in self if func(s[col])])

	def reduce (self, func):
		"""
		Alias of python builtin `reduce`
		@params:
			`func`: the function
		@returns:
			The reduced value
		"""
		return utils.reduce(func, self)
		
	def reduceCol (self, func, col = 0):
		"""
		Reduce a column
		@params:
			`func`: the function
			`col`: the column to reduce
		@returns:
			The reduced value
		"""
		return utils.reduce(func, [s[col] for s in self])
	
	def rbind (self, *rows):
		"""
		The multiple-argument versoin of `rbind`
		@params:
			`rows`: the rows to be bound to Channel
		@returns:
			The combined Channel
			Note, self is also changed
		"""
		width = self.width()
		rows2 = [s for s in self]
		for row in rows:
			if isinstance(row, Channel):
				if row.width() == 1:
					rows2.extend([r * max(width, 1) for r in row])
				elif row.width() != width and width != 0:
					raise ValueError('Unable to rbind unequal width channels (%s, %s)' % (width, row.width()))
				else:
					rows2.extend(row)
			elif isinstance(row, tuple) or isinstance(row, list):
				lrow = len(row)
				if lrow == 1:
					row = row * max(width, 1)
					lrow = width
				if lrow != width and width != 0:
					raise ValueError('Cannot bind row (width: %s) to Channel (width: %s).' % (lrow, width))
				rows2.append(tuple(row))
			else:
				rows2.append((row, ) * max(width, 1))
		return Channel.create(rows2)
	
	def insert (self, cidx, *cols):
		"""
		Insert columns to a channel
		@params:
			`cidx`: Insert into which index of column?
			`cols`: the columns to be bound to Channel
		@returns:
			The combined Channel
			Note, self is also changed
		"""
		ret = self
		if not ret:
			if cidx != 0 and cidx is not None and cidx != -1:
				raise ValueError('Cannot insert a column other than 0 into an empty channel.')
			ret  = [()] * (len(cols[0]) if isinstance(cols[0], tuple) or isinstance(cols[0], list) else 1)
		length = len(ret)
		if cidx is None:
			colsbefore = ret
			colsafter  = []
		else:
			colsbefore = [s[:cidx] for s in ret]
			colsafter  = [s[cidx:] for s in ret]
		for col in cols:
			if not col: continue
			if isinstance(col, Channel):
				if len(col) == 1:
					col = col * length
			elif isinstance(col, tuple) or isinstance(col, list):
				lcol = len(col)
				if lcol == 1:
					col = col * length
					lcol = length
				if lcol != length:
					raise ValueError('Cannot bind column (length: %s) to Channel (length: %s).' % (lcol, length))
				col = [(c,) for c in col]
			else:
				col = [(col,)] * length
			
			colsbefore = [colsbefore[i] + c if colsbefore else c for i, c in enumerate(col)]
				
		return Channel.create([col + colsafter[i] if colsafter else col for i, col in enumerate(colsbefore)])
		
	def cbind(self, *cols):
		"""
		Add columns to the channel
		@params:
			`cols`: The columns
		@returns:
			The channel with the columns inserted.
		"""
		return self.insert(None, *cols)
	
	def colAt (self, index):
		"""
		Fetch one column of a Channel
		@params:
			`index`: which column to fetch
		@returns:
			The Channel with that column
		"""
		return self.slice (index, 1)
	
	def slice (self, start, length = None):
		"""
		Fetch some columns of a Channel
		@params:
			`start`:  from column to start
			`length`: how many columns to fetch, default: None (from start to the end)
		@returns:
			The Channel with fetched columns
		"""
		return Channel.create([s[start:start + length] for s in self]) if length else \
			   Channel.create([s[start:] for s in self])
	
	def fold (self, n = 1):
		"""
		Fold a Channel. Make a row to n-length chunk rows
		```
		a1	a2	a3	a4
		b1	b2	b3	b4
		if n==2, fold(2) will change it to:
		a1	a2
		a3	a4
		b1	b2
		b3	b4
		```
		@params:
			`n`: the size of the chunk
		@returns
			The new Channel
		"""
		if self.width() % n != 0:
			raise ValueError ('Failed to fold, the width %s cannot be divided by %s' % (self.width(), n))
		
		nrows = int(self.width() / n)
		ret = []
		for row in self:
			for i in [x*n for x in range(nrows)]:
				ret.append (row[i:i+n])
		return Channel.create(ret)
	
	def unfold (self, n = 2):
		"""
		Do the reverse thing as self.fold does
		@params:
			`n`: How many rows to combind each time. default: 2
		@returns:
			The unfolded Channel
		"""
		if len(self) % n != 0:
			raise ValueError ('Failed to unfold, the length %s cannot be divided by %s' % (len(self), n))
		
		nrows = int(len(self) / n)
		ret = []
		for i in range(nrows):
			r = ()
			for j in range(n):
				r += self[i*n + j]
			ret.append(r)
		return Channel.create(ret)		
	
	def split (self, flatten=False):
		"""
		Split a Channel to single-column Channels
		@returns:
			The list of single-column Channels
		"""
		return [ self.colAt(i).flatten() for i in range(self.width()) ] if flatten else \
			   [ self.colAt(i) for i in range(self.width()) ]

	def attach(self, *names):
		"""
		Attach columns to names of Channel, so we can access each column by:
		`ch.col0` == ch.colAt(0)
		@params:
			`names`: The names. Have to be as length as channel's width. None of them should be Channel's property name
		"""
		flatten = False
		if isinstance(names[-1], bool):
			flatten = names[-1]
			names   = names[:-1]
		mywidth = self.width()
		lnames  = len(names)
		if mywidth != lnames:
			raise ValueError('Lenth of names are different frome the width of the channel.')
		for i, name in enumerate(names):
			if hasattr(self, name) and not isinstance(getattr(self, name), Channel) and not isinstance(getattr(self, name), list):
				raise ValueError('Cannot attach column to "%s" as it is already a property of Channel.' % name)
			setattr(self, name, self.colAt(i).flatten() if flatten else self.colAt(i))
	
	def flatten (self, col = None):
		"""
		Convert a single-column Channel to a list (remove the tuple signs)
		`[(a,), (b,)]` to `[a, b]`
		@params:
			`col`: The column to flat. None for all columns (default)
		@returns:
			The list converted from the Channel.
		"""
		return [item for sublist in self for item in sublist] if col is None else \
			   [sublist[col] for sublist in self]
