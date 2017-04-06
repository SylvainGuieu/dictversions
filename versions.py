
try:
    unicode
except NameError: # python 3
    def iteritems(d):
        return iter(d.items())
    def iterkeys(d):
        return iter(d.keys())
    def itervalues(d):
        return iter(d.values())
    def keys(d):
        return list(d.keys())
    def values(d):
        return list(d.values())
    def items(d):
        return list(d.items())

    _p2 = False
else:
    def iteritems(d):
        return d.iteritems()
    def iterkeys(d):
        return d.iterkeys()
    def itervalues(d):
        return d.itervalues()
    def keys(d):
        return d.keys()
    def values(d):
        return d.values()
    def items(d):
        return d.items()
    _p2 = True


ROOTVERSION = None
ROOTBRANCH  = None
ROOTPATCH   = None

dtype_help = """
        dtype : callable, optional
            dtype is used to create the child dictionary
            dtype is called without argument and must return a dict like object 
            default is dict
"""
patch_help = {
"description" : """
        A created patch is on top of all versions. Every items created int the patch overwrite
        the one created on *any* version.
        But contrary to branches, changing to `patch2` from `patch1` jump to `patch2`. 
        Meaning that `patch2` and `patch1` are at the same level.

        Changing the version when within a patch do not change the patch version but instead
        change the underneath object version.

        If the patch description is None, it means no patch.
""",
"notecreation": """
        **Note** If the patch does not exists it will be created on the fly and stored 
        use new_patch and get_patch, has_patch for more control        
""", 
"seealso": """      methods: new_patch, get_patch, remove_patch, has_patch
                branch, version
""", 
"dtype":dtype_help, 
"patch": """
        patch : hashable
            any hashable object that define the patch description        
"""        
}

branch_help = {
"description" : """
        A branch is derived from a version. Every items created int the branch overwrite
        the one created on the parent version.

        A branch can be sub-branched indefinitely. A version of a branch can also be changed

        Changing the version when within a branch change the branch version not the parent
        version.

""",
"notecreation": """
        **Note** If the branch does not exists it will be created on the fly and stored. 
        use new_branch and get_branch, has_branch for more control        
""", 
"seealso": """          methods: new_branch, get_branch, remove_branch, has_branch
            patch, version
""", 
"dtype":dtype_help, 
"branch": """
        branch : hashable
            any hashable object that define the branch description        
"""        
}
version_help = {
"description" : """
        A version is a collection of item independent from one to an other. Two versions
        of the same VersionnedDict object are at the same level (different trunc) contrary to branch.
                                        
""",
"notecreation": """
        **Note** If the version does not exists it will be created on the fly and stored. 
        use new_version and get_version, has_version for more control        
""", 
"seealso": """          methods: new_version, get_version, remove_version, has_version
            patch, branch
""", 
"dtype":dtype_help, 
"version": """
        version : hashable
            any hashable object that define the version description        
"""        
}






def _parse_empty(v,d):
    if d is None:
        return v.d.__class__
    if isinstance(d, type):
        return d
    return d.__class__


class VersionItems(object):
    def __init__(self,v):
        self.v = v
    def __iter__(self):
        return VersionItemsIterator(iteritems(self.v.d), self.v.parent())

class VersionItemsIterator(object):        
    def __init__(self, iterator, parent ):
        self.iterator = iterator
        self.parent = parent
        self.founds = set()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            key, value = next(self.iterator)
        except StopIteration:
                
                if self.parent is not None:
                   p = self.parent
                   self.iterator = iteritems(p.d)
                   self.parent = p.parent()
                   return self.__next__()
                else:
                    raise StopIteration            

        else:
            if key in self.founds:
                return self.__next__()
            else:
                self.founds.add(key) 
            return key, value         
    if _p2:
        next = __next__

class VersionKeys(object):
    def __init__(self,v):
        self.v = v
    def __iter__(self):
        return VersionKeysIterator(iterkeys(self.v.d), self.v.parent()) 

class VersionKeysIterator(object):
    def __init__(self, iterator, parent ):
        self.iterator = iterator
        self.parent = parent
        self.founds = set()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            key = next(self.iterator)
        except StopIteration:            
                if self.parent is not None:
                   p = self.parent
                   self.iterator = iterkeys(p.d)
                   self.parent = p.parent()
                   return self.__next__()
                else:
                    raise StopIteration            

        else:
            if key in self.founds:
                return self.__next__()
            else:
                self.founds.add(key) 
            return key
    if _p2:
        next = __next__


class VersionValues(object):
    def __init__(self,v):
        self.v = v
    def __iter__(self):
        return VersionValuesIterator(iteritems(self.v.d), self.v.parent()) 


class VersionValuesIterator(object):
    def __init__(self, iterator, parent ):
        self.iterator = iterator
        
        self.parent = parent
        self.founds = set()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            key, value = next(self.iterator)
        except StopIteration:            
                if self.parent is not None:
                   p = self.parent
                   self.iterator = iteritems(p.d)
                   self.parent = p.parent()
                   return self.__next__()
                else:
                    raise StopIteration
        else:
            if key in self.founds:
                return self.__next__()
            else:
                self.founds.add(key) 
            return value 
    if _p2:
        next = __next__    


D, CV, CB, CP, VERSIONS, PATCHES, PARENT = range(7)

class VersionBuild(tuple):
    def __new__(cls, d, cv, cb, cp, versions, pathes, parent):
        return tuple.__new__(cls, (d, cv, cb, cp, versions, pathes, parent))
    
    @classmethod
    def new(cls, d, version=ROOTVERSION, parent=None):
        return cls(d, version, ROOTBRANCH, ROOTPATCH, {version:(d,{})} , {}, parent)

    @classmethod
    def get_or_make_branch(cls, branch, parent, empty=dict):
        branches = parent[VERSIONS][parent[CV]][1]
        try:
            d = branches[branch]
        except KeyError:
            d = empty()
            branches[branch] = d
        return cls(d, parent[CV], branch, parent[CP], {ROOTVERSION:({},{})}, {}, parent)

    @classmethod
    def make_branch(cls, branch, parent, empty=dict):
        branches = parent[VERSIONS][parent[CV]][1]
        try:
            branches[branch]
        except KeyError:
            pass
        else:
            raise ValueError("branch %r already exists"%branch)
        d = empty()
        branches[branch] = d
        return cls(d, parent[CV], branch, parent[CP], {ROOTVERSION:({},{})}, {}, parent)        

    @classmethod
    def get_branch(cls, branch, parent, empty=dict):
        branches = parent[VERSIONS][parent[CV]][1]
        try:
            d = branches[branch]
        except KeyError:
            raise ValueError("branch %r does not exists"%branch)
        return cls(d, parent[CV], branch, parent[CP], {ROOTVERSION:({},{})}, {}, parent)


    @classmethod
    def get_or_make_version(cls, version, parent, empty=dict):
        
        versions = parent[VERSIONS]
        try:
            d = versions[version][0]
        except KeyError:
            d = empty()
            versions[version] = (d, {})
        ##
        # if a patch change the version of 
        # the second dictionary on patch 
        if isinstance(parent[D], Patch):
            d = Patch(parent[D].d, d)

        return cls(d, version, parent[CB], parent[CP], versions, parent[PATCHES], parent[PARENT])


    @classmethod
    def make_version(cls, version, parent, empty=dict):   
        versions = parent[VERSIONS]
        try:
            versions[version][0]
        except KeyError:
            pass
        else:
            raise ValueError("version %r already exists"%version)    
        
        d = empty()
        versions[version] = (d, {})
        ##
        # if a patch change the version of 
        # the second dictionary on patch 
        if isinstance(parent[D], Patch):
            d = Patch(parent[D].d, d)
        return cls(d, version, parent[CB], parent[CP], versions, parent[PATCHES], parent[PARENT])

    @classmethod
    def get_version(cls, version, parent, empty=dict):
        
        versions = parent[VERSIONS]
        try:
            d = versions[version][0]
        except KeyError:
            raise ValueError("version %r does not exists"%version) 
                    
        ##
        # if a patch change the version of 
        # the second dictionary on patch 
        if isinstance(parent[D], Patch):
            d = Patch(parent[D].d, d)

        return cls(d, version, parent[CB], parent[CP], versions, parent[PATCHES], parent[PARENT])


    @classmethod
    def get_or_make_patch(cls, patch, parent, empty=dict):
        if patch is ROOTPATCH:
            ## remove the patch
            d = parent[VERSIONS][parent[CV]]
            return cls(d, parent[CV], parent[CB], patch, parent[VERSIONS], parent[PATCHES], parent[PARENT])

        patches = parent[PATCHES]
        try:
            d = patches[patch]
        except KeyError:
            d = empty()            
            patches[patch] = d

        p = Patch(d, parent[VERSIONS][parent[CV]][0])
        return cls(p, parent[CV], parent[CB], patch, parent[VERSIONS], parent[PATCHES], parent[PARENT])

    @classmethod
    def make_patch(cls, patch, parent, empty=dict):
        if patch is ROOTPATCH:
            ## remove the patch
            d = parent[VERSIONS][parent[CV]]
            return cls(d, parent[CV], parent[CB], patch, parent[VERSIONS], parent[PATCHES], parent[PARENT])

        patches = parent[PATCHES]
        try:
            patches[patch]
        except KeyError:
            pass
        else:
            raise ValueError("patch %r already exists"%patch) 

        d = empty()            
        patches[patch] = d

        p = Patch(d, parent[VERSIONS][parent[CV]][0])
        return cls(p, parent[CV], parent[CB], patch, parent[VERSIONS], parent[PATCHES], parent[PARENT])

    @classmethod
    def get_patch(cls, patch, parent, empty=dict):
        if patch is ROOTPATCH:
            ## remove the patch
            d = parent[VERSIONS][parent[CV]]
            return cls(d, parent[CV], parent[CB], patch, parent[VERSIONS], parent[PATCHES], parent[PARENT])

        patches = parent[PATCHES]
        try:
            d = patches[patch]
        except KeyError:
            raise ValueError("patch %r does not exists"%patch) 

        patches[patch] = d
        p = Patch(d, parent[VERSIONS][parent[CV]][0])
        return cls(p, parent[CV], parent[CB], patch, parent[VERSIONS], parent[PATCHES], parent[PARENT])



class PatchKeys(object):
    def __init__(self, *args):
        self.ds = args

    def __iter__(self):
        return PatchKeysIterator([iterkeys(d) for d in self.ds])

class PatchKeysIterator(object):
    def __init__(self, iterators):
        self.iterators = iterators
        self.i  = 0
        self.found = set()

    def __iter__(self):
        return self
        
    def __next__(self):

        try:
            key = next(self.iterators[self.i])
        except IndexError:
            raise StopIteration
        except StopIteration:
            self.i += 1
            return self.__next__()

        if key in self.found:
            return self.__next__()
        self.found.add(key)
        return key
    if _p2:
        next = __next__


class PatchValues(object):
    def __init__(self, *args):
        self.ds = args

    def __iter__(self):
        return PatchValuesIterator([iteritems(d) for d in self.ds])

class PatchValuesIterator(object):
    def __init__(self, iterators):
        self.iterators = iterators
        self.i  = 0
        self.found = set()

    def __iter__(self):
        return self

    def __next__(self):

        try:
            key, value = next(self.iterators[self.i])
        except IndexError:
            raise StopIteration
        except StopIteration:
            self.i += 1
            return self.__next__()

        if key in self.found:
            return self.__next__()
        self.found.add(key)
        return value
    if _p2:
        next = __next__

class PatchItems(object):
    def __init__(self, *args):
        self.ds = args

    def __iter__(self):
        return PatchItemsIterator([iteritems(d) for d in self.ds])

class PatchItemsIterator(object):
    def __init__(self, iterators):
        self.iterators = iterators
        self.i  = 0
        self.found = set()

    def __iter__(self):
        return self

    def __next__(self):

        try:
            key, value = next(self.iterators[self.i])
        except IndexError:
            raise StopIteration
        except StopIteration:
            self.i += 1
            return self.__next__()

        if key in self.found:
            return self.__next__()
        self.found.add(key)
        return key, value
    if _p2:
        next = __next__



class Patch(object):
    """ a patch object use 2 dictionary like objects the first one is a patch 

    all writing operations clear, pop, D[k] = v, update, are done on the patch
    all read operation get, D[k] are first done on the patch and if the key is not found 
    it is done on the master.      
    """
    def __init__(self, d, d2):
        """ dictionary like object which can patch a master dictionary 
        
        Parameters
        ----------
        d :  dictionary like (must have the keys method)
            the patch 
        d2 : dictionary like (must have the keys method)
            the master 

        Example
        -------
            >>> d = {"x":1, "y":2}
            >>> p = Patch({"x":99}, d)
            >>> p['x']
            99
            >>> p['y']
            2
            >>> del p['x']
            >>> p['x']
            1
        """
        self.d = d
        self.d2 = d2
    def __getitem__(self, item):
        try:
            return self.d[item]
        except KeyError:
            return self.d2[item]
    def __setitem__(self, item, value):
        self.d[item] = value
    
    def __contains__(self, key):
        if key in self.d:
            return True        
        return key in self.d2

    def __iter__(self):
        return iter(PatchKeys(self))

    def __len__(self):
        s = set(iterkeys(self.d))
        s.update( set(iterkeys(self.d2)))
        return len(s)       

    def __eq__(self, right):
        if self._build == getattr(right, "_build", None):
            return True

        if len(self)!=len(right):
            return False
        
        return dict(self)==right

        # for k,v in iteritems(self):            
        #     try:
        #         vr = right[k]
        #     except KeyError:
        #         return False
        #     if v!=vr:
        #         return False
        # return True

    def has_key(self, key):
        """ -> True if key in D """
        return key in self

    def __delitem__(self, key):
        del self.d[key]

    def pop(self,*args):
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
        If key is not found, d is returned if given, otherwise KeyError is raised
        
        If the data older object has the pop attribute it is called directly

        *NOTE* the key is remove on the current patch
                this can have an important side effect:
            
            >>> p = Patch({"x":100}, {"x":1})
            >>> p['x']
            100
            >>> p.pop("x")
            100
            >>> p['x']   ## 'x' still exists but have the value of the parent
            1 
        """
        try:
            _p = self.d.pop
        except AttributeError:
            pass
        else:
            return _p(*args)
       
        if len(args)==1:
            key, = args
            value = self.d[key]
            del self.d[key]
            return value

        if len(args)>2:
            raise TypeError("pop takes only 1 or 2 arguments")

        key,default = args
        try:
            value = self.d[key]
            del self.d[key]
        except KeyError:
            return default
        else:
            return value

    def clear(self):
        """ D.clear() -> None.  Remove all items from D. 

        *NOTE* this clear the current patch, not the parent version.
            
            >>> p = Patch(dict(x=99) ,dict(x=10, y=100))            
            >>> list(p.items())
            [('x', 99), ('y', 100)]
            >>> p.clear()
            >>> list(p.items())
            [('y', 100), ('x', 10)]                                    
        """
        try:
            _c = self.d.clear
        except AttributeError:
            d = self.d
            for k in d.keys():
                del d[k]
        else:
            return _c()


    def get(self,key, default=None):
        """ D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None."""    
        try:
            return self[key]
        except KeyError:
            return default 

    def update(self, __d__={}, **kwargs):
        """
        D.update([E, ]**F) -> None.  Update D from dict/iterable E and F.
        If E present and has a .keys() method, does:     for k in E: D[k] = E[k]
        If E present and lacks .keys() method, does:     for (k, v) in E: D[k] = v
        In either case, this is followed by: for k in F: D[k] = F[k]

        """
        try:
            _u = self.d.update
        except AttributeError:
            for k,v in iteritems(dict(__d__,**kwargs)):
                self.d[k] = v
        else:
            return _u(__d__, **kwargs)
         

    def setdefault(self, key, default):
        """  D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D 
                
        """
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default
    if _p2:
        def iteritems(self):
            return PatchItems(self.d, self.d2)

        def items(self):
            return list(self.iteritems())

        def iterkeys(self):
            return PatchKeys(self.d, self.d2)

        def keys(self):
            return list(self.iterkeys())

        def itervalues(self):
            return PatchValues(self.d, self.d2)

        def values(self):
            return list(self.itervalues())

    else:
        def items(self):
            return PatchItems(self.d, self.d2)
            
        def keys(self):
            return PatchKeys(self.d, self.d2)
            
        def values(self):
            return PatchValues(self.d, self.d2)


class VersionnedDict(object):
    """ dictionary like object with versioning capabilities 
    
    >>> data = Version({'x':10, 'y':100})
    >>> data['x']
    10
    >>> other_data = data.branch('other', y=-100)
    >>> other_data['x']
    10
    >>> other_data['y']
    -100
    >>> data['y']
    100
    >>> data.branch(2.0)['x'] = -10
    >>> data.branch(2.0)['x']
    -10
    """    
    _parent = None
    current_branch = ROOTBRANCH
    current_patch  = ROOTPATCH
    def __init__(self, d=None, version=ROOTVERSION):
        """ versioned dictionary like object 

        from the created object one can create two things:
            - a new independent version
            - a dependant branch, items not set in the branch is taken 
              from the parent version


        
        Parameters
        ----------
        d : dict like
            if None a dictionary is create
            dictionary like object. It must init like a dict.
            when creating empty dictionary inside the Version (new version or new branch)
            the new dictionary will be created by d.__class__()
        
        version : any hashable, optional
            set the version of the created Version object, default is None
                
        
        Examples
        --------
        
        Example of use for plotting 
    
            main = VersionnedDict({{'color':'red', 'linestyle':'solid', 'xlabel':'Time', 'ylabel':''}})
            mainsoft = main.version('soft', main, color="black", linestyle="dot")
            
            pressure = main.branch('pressure', x=#DATA#,  y=#DATA# , ylabel="pressure [mBar]" )
            temp     = mainsoft.branch('temp', x=#DATA#,  y=#DATA# , ylabel="Temperature [K]" )

            plot(**pressure) # plot is plotting the data
            plot(**temp)
        
        Example of use in data processing
            
            D = VersionnedDict({{}},version=1) # create a new object with version=1
            
            with open("result_2017-03-01.dat") as f:
                D.version(1, data=f.read(), date="2017-03-01")
            
            with open("result_2017-02-21.dat") as f:
                D.version(2, data=f.read(), date="2017-02-21")
            
            
            ### play with D
            D.change_version(2)

            ### play with D again
            
            ### compare two versions: 
            
            D.version(1)['data'] != D.version(2)['data'] 
            
        

        """
        if isinstance(d, VersionBuild):
            self._build = d            
        else:                      
            self._build = VersionBuild.new({} if d is None else d, version=version)

        ##
        # set here what will be acced ofthen 
        self.d = self._build[D] 
        self._parent = self.C(self._build[PARENT]) if self._build[PARENT] else None


    
    def patches(self):
        """ available patches """
        return keys(self._build[PATCHES])

    @property
    def current_patch(self):
        """ current patch of the object """
        return self._build[CP]
    
    def branches(self):
        """ available sub-branches """
        return keys(self._build[VERSIONS][self._build[CV]][1])

    @property
    def current_branch(self):
        """ current branch of the object """
        return self._build[CB]

    
    def versions(self):
        """ current version of the object """
        return keys(self._build[VERSIONS])

    @property
    def current_version(self):
        """ current version of the object """
        return self._build[CV]

    def iscloneof(self, obj):
        """ check if a given object is a clone of itself 

        Parameter
        ---------
        obj : any
            mostly a VersionnedDict object

        Example
        -------
            >>> v = VersionnedDict({})
            >>> b1 = v.branch('test branch')
            >>> b2 = v.branch('test branch')
            >>> b1 is b2
            False
            >>> b1 == b2
            True
            >>> b2.iscloneof(b1)
            True
            >>> b1.iscloneof(b2)
            True

        """
        return self._build is getattr(obj, "_build", None)     

    def parent(self):
        """ Return the parent version (the trunk) or None
        
        VersionnedDict object has parent if they have been branched
        
        *Note* that the returned object is a clone of the real parent 
        therefore :  
            - `v.branch(2).parent() is v` return False  
            - `v.branch(2).parent() == v` return True
            - any changes in `v.branch(2).parent()` will affect `v`       
        
        Example
        -------
                >>> v = VersionnedDict({{'x':1}})
                >>> v.branch(2.0).parent() == v
                True
                >>> v.branch(2).parent() is v
                False
                >>> v.branch(2).parent()['x'] = 10
                >>> v['x']
                10

        See Also
        --------
        root : return the root version
        """
        return self._parent        

    def root(self):
        """ return the root version object 
        
        *Note* that the returned object is a clone of the real root 
        therefore :  
            - `r.branch(2).branch(0.1).root() is r` return False  
            - `r.branch(2).branch(0.1).root() == r` return True
            - any changes in `r.branch(2).branch(0.1).root()` will affect `r`
        """
        p = self._build[PARENT]
        if p is None:
            return self.C(self._build)

        while True:
            _p = p[PARENT]
            if _p is None:
                return self.C(p)
            p = _p

    def __str__(self):
        return dict(self).__str__()

    def __repr__(self):
        return dict(self).__repr__()

    def __len__(self):
        return len(keys(self))
           
    def __eq__(self, right):
        #if len(self)!=len(right):
        #    return False

        return dict(self)==right
        #     try:
        #         vr = right[k]
        #     except KeyError:
        #         return False
        #     if v!=vr:
        #         return False
        # return True

    def __getitem__(self, item):
        try:
            return self.d[item]
        except KeyError:

            p = self.parent()
            if p is not None:
                return p[item]
            else:
                raise KeyError('%r'%item)        

    def __setitem__(self, item, value):
        self.d[item] = value

    def __contains__(self, key):
        if key in self.d:
            return True        
        ##
        # Try with the parent 
        p = self.parent()
        if p is not None:
            return key in p
        return False
    
    @property
    def C(self):
        return self.__class__

    def __iter__(self):
        return iter(VersionKeys(self))    

    def __delitem__(self, key):
        del self.d[key]


    def has_key(self, key):
        """ -> True if key in D """
        return key in self


    def pop(self,*args):
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
        If key is not found, d is returned if given, otherwise KeyError is raised
        
        If the data older object has the pop attribute it is called directly

        *NOTE* the key is remove on the current version/branch/patch
               if D is branched or patched this can have an important side effect:
            
            >>> v = VersionnedDict({"x":1})
            >>> b = v.branch("modified X"  , x=100)
            >>> b['x']
            100
            >>> b.pop("x")
            100
            >>> b['x']   ## 'x' still exists but have the value of the parent version
            1 
        """
        try:
            _p = self.d.pop
        except AttributeError:
            if len(args)==1:
                key, = args
                value = self.d[key]
                del self.d[key]
                return value

            if len(args)>2:
                raise TypeError("pop takes only 1 or 2 arguments")

            key,default = args
            try:
                value = self.d[key]
                del self.d[key]
            except KeyError:
                return default
            else:
                return value    
        else:
            return _p(*args)
       
    def clear(self):
        """ D.clear() -> None.  Remove all items from D. 

        *NOTE* this clear the current branch, not the parent version.

            >>> v = VersionnedDict(dict(x=10, y=100))
            >>> b = v.branch('test', x=99)
            >>> list(b.items())
            [('x', 99), ('y', 100)]
            >>> b.clear()
            >>> list(b.items())
            [('y', 100), ('x', 10)]                                    
        """
        try:
            _c = self.d.clear
        except AttributeError:
            d = self.d
            for k in d.keys():
                del d[k]
        else:
            return _c()

    def get(self,key, default=None):
        """ D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None."""        
        try:
            return self[key]
        except KeyError:
            return default 

    def change_patch(self, patch, __d__={}, **kwargs):
        """ change the patch of the object in place 

        {description}
        
        {notecreation}
                
        Parameters
        ----------
        {patch}
        __d__ : dict like, optional 
            update the patch with this dictionary 
        **kwargs : dict like, optional 
            update the patch with this dictionary 

        See Also
        --------
        {seealso}

        """.format(**patch_help)

        self.C.__init__(self,VersionBuild.get_or_make_patch(patch, self._build,  empty=self.empty))
        self.update(__d__, **kwargs)


    def patch(self, patch, __d__={}, **kwargs):
        """ return a given patch, create one if needed
        
        {description}
        
        {notecreation}
    
        Parameters
        ----------
        {patch}
        __d__ : dict like, optional 
            update the patch with this dictionary 
        **kwargs : dict like, optional 
            update the patch with this dictionary  
        
        Outputs
        -------
        patched : a Verions object with the patched state
        

        Example
        -------
            >>> v = VersionnedDict(dict(x=1,y=10), 1.0)
            >>> v.version(2.0).update(x=2, y=20)
            >>> p = v.version(1.0).patch("xcorrected",  x=0)
            >>> p['x']
            0 
            >>> p['y']
            10
            >>> p.version(2.0)['y']
            20
            >>> p.version(2.0)['x']
            0
            >>> p.patch(None)


        See Also
        --------
        {seealso}               
        """.format(**patch_help)

        new = self.C(VersionBuild.get_or_make_patch(patch, self._build,  empty=self.empty))
        new.update(__d__, **kwargs)
        return new

    def get_patch(self, patch):
        """ return a previously created patch 

        {description}

        Parameters
        ----------
        {patch}
    
        Outputs
        -------
        patched : a Verions object with the patched state
        
        Raises
        ------
        ValueError : if the patch does not exists

        See Also
        --------
        {seealso}  
        """.format(**patch_help)

        return self.C.__init__(self,VersionBuild.get_patch(patch, self._build,  empty=self.empty))

    def new_patch(self, patch, dtype=None):
        """ create a new patch and return it 

        {description}

        Parameters
        ----------
        {patch}
        {dtype}

        Outputs
        -------
        patched : a Verions object with the patched state
        
        Raises
        ------
        ValueError : if the patch does not exists

        See Also
        --------
        {seealso}  
        """.format(**patch_help)

        return self.C.__init__(self,VersionBuild.make_patch(patch, self._build,  empty=dtype or self.empty))

    def remove_patch(self, patch):
        """ remove an existing patch

        Parameters        
        ----------
        {patch}

        Raises
        ------
        RuntimeError :  if the patch one want to delete is the one active in the object
        ValueError : if the patch does not exists 

        See Also
        --------
        {seealso}
        """.format(**patch_help)

        if self.current_patch == patch:
            raise RuntimeError("patch %r currently in used by this object"%patch)
        try:
            del self._build[PATCHES][patch]
        except KeyError:
            raise ValueError("patch %r does not exists"%patch)

    def has_patch(self, patch):
        """ check is a patch exists 

        Parameters        
        ----------
        {patch}
        
        Outputs
        -------
        test : bool
            True is the patch exists

        See Also
        --------
        {seealso}
        """.format(**patch_help)
        return patch in self._build[PATCHES]

    def change_branch(self, branch, __d__={}, **kwargs):
        """ change the branch of the object in place 
        
        {description}
        
        {notecreation}
                        
        Parameters
        ----------
        {branch}
        __d__ : dict like, optional 
            update the branch with this dictionary 
        **kwargs : dict like, optional 
            update the branch with this dictionary 
        
        See Also
        --------
        {seealso}

        """.format(**branch_help)

        self.C.__init__(self, VersionBuild.get_or_make_branch(branch, self._build,  empty=self.empty))
        self.update(__d__, **kwargs)        
        
    def branch(self, branch, __d__={}, **kwargs):
        """ return a branch of the object, create it if does not exists
        
        {description}
        
        {notecreation}
                        
        Parameters
        ----------
        {branch}
        __d__ : dict like, optional 
            update the branch with this dictionary 
        **kwargs : dict like, optional 
            update the branch with this dictionary 
        
        Outputs
        -------
        branched : Version
            branched Version object.
            note:  v.branch(2.0) == v.branch(2.0) -> True
                   v.branch(2.0) is v.branch(2.0) -> False
        
        Example
        -------
        
            main = Version({{'color':'red', 'linestyle':'solid', 'xlabel':'Time', 'ylabel':''}})
            mainsoft = main.version('soft', main, color="black", linestyle="dot")
            
            pressure = main.branch('pressure', x=#DATA#,  y=#DATA# , ylabel="pressure [mBar]" )
            temp     = mainsoft.branch('temp', x=#DATA#,  y=#DATA# , ylabel="Temperature [K]" )
            
            plot(**pressure) # plot is plotting the data
            plot(**temp)

        See Also
        --------
        {seealso}

        """.format(**branch_help)

        new = self.C(VersionBuild.get_or_make_branch(branch, self._build, empty=self.empty))
        new.update(__d__, **kwargs)
        return new       

    def new_branch(self, branch, dtype=None):
        """ create and return a new branch
        
        {description}
                                
        Parameters
        ----------
        {branch}
        {dtype}

        See Also
        --------
        {seealso}
        

        """.format(**branch_help)
        return self.C(VersionBuild.make_branch(branch, self._build, empty=dtype or self.empty))

    def get_branch(self, branch):
        """ return a previously created branch
        
        {description}
                                
        Parameters
        ----------
        {branch}
        
        Raises
        ------
        ValueError : if the branch does not exists

        See Also
        --------
        {seealso}
        

        """.format(**branch_help)        
        return self.C(VersionBuild.get_branch(branch, self._build, empty=self.empty))

    def remove_branch(self, branch):
        """ remove a previously created sub branch
                                                
        Parameters
        ----------
        {branch}
        
        Raises
        ------
        ValueError : if the branch does not exists
        
        See Also
        --------
        {seealso}
        

        """.format(**branch_help)    
        b = self._build
        try:
            del b[VERSIONS][b[CV]][1][branch]
        except KeyError:
            raise ValueError("branch %r does not exists"%branches)

    def has_branch(self, branch):
        """ check is a sub branch exists 

        Parameters        
        ----------
        {branch}
        
        Outputs
        -------
        test : bool
            True is the branch exists

        See Also
        --------
        {seealso}
        """.format(**branch_help)

        b = self._build
        return branch in b[VERSIONS][b[CV]][1]

    def change_version(self, version, __d__={}, **kwargs):
        """ change the version of the object in place 
        
        {description}
        
        {notecreation}
                        
        Parameters
        ----------
        {version}
        __d__ : dict like, optional 
            update the version with this dictionary 
        **kwargs : dict like, optional 
            update the version with this dictionary 
        
        See Also
        --------
        {seealso}

        """.format(**version_help)
        self.C.__init__(self, VersionBuild.get_or_make_version(version, self._build, empty=self.empty))
        self.update(__d__, **kwargs)
    
    def version(self, version, __d__={}, **kwargs):
        """ return a version of the object, create it if does not exists
        
        {description}
        
        {notecreation}
                        
        Parameters
        ----------
        {version}
        __d__ : dict like, optional 
            update the version with this dictionary 
        **kwargs : dict like, optional 
            update the version with this dictionary 
        
        Outputs
        -------
        versioned : Version
            versioned Version object.
            note:  v.version(2.0) == v.version(2.0) -> True
                   v.version(2.0) is v.version(2.0) -> False
        
        Example
        -------
            
            >>> v = Verions({{"x":1}}, 1)
            >>> list(v.keys())
            ["x"]
            >>> v2 = v.version(2)
            >>> list(v.keys())
            []
            >>> v1.version(1) == v
            True


        See Also
        --------
        {seealso}

        """.format(**version_help)
        new = self.C(VersionBuild.get_or_make_version(version, self._build, empty=self.empty))
        new.update(__d__, **kwargs)
        return new    

    def new_version(self, version, dtype=None):  
        """ create and return a new version
        
        {description}
                              
        Parameters
        ----------
        {version}
        {dtype}

        See Also
        --------
        {seealso}
        

        """.format(**version_help)
        return self.C(VersionBuild.make_version(version, self._build, empty=(dtype or self.empty)))

    def get_version(self, version):
        """ return a previously created version
        
        {description}
                                
        Parameters
        ----------
        {version}
        
        Raises
        ------
        ValueError : if the version does not exists

        See Also
        --------
        {seealso}
        

        """.format(**version_help)   
        return self.C(VersionBuild.get_version(version, self._build))

    def remove_version(self, version):
        """ remove an existing version

        Parameters        
        ----------
        {version}

        Raises
        ------
        RuntimeError :  if the version one want to delete is the one active in the object
        ValueError : if the version does not exists 
        
        See Also
        --------
        {seealso}
        """.format(**version_help)
        if self.current_version == version:
            raise RunTimeError("version %r currently in used by this object"%version)
        try:
            del self._build[VERSIONS][version]
        except KeyError:
            raise ValueError("version %r does not exists"%version)

    def has_version(self, version):        
        """ check is a version exists 
        
        Parameters        
        ----------
        {version}
        
        Outputs
        -------
        test : bool
            True is the version exists

        See Also
        --------
        {seealso}
        """.format(**version_help)

        return version in self._build[VERSIONS]

    def empty(self):
        """ create an empty dictionary like object 

        the class of the dictionary is the class the current dictionary 
        stored in the version.
        """
        return  self.d.__class__()        

    def update(self, __d__={}, **kwargs):
        """
        D.update([E, ]**F) -> None.  Update D from dict/iterable E and F.
        If E present and has a .keys() method, does:     for k in E: D[k] = E[k]
        If E present and lacks .keys() method, does:     for (k, v) in E: D[k] = v
        In either case, this is followed by: for k in F: D[k] = F[k]

        The update is done one the current version/branch/patch
        
        Note that if the dictionary data holder has the 'update' attribute it will be 
        called directly to proceed.
        """
        try:
            _u = self.d.update
        except AttributeError:
            for k,v in iteritems(dict(__d__,**kwargs)):
                self.d[k] = v
        else:
            return _u(__d__, **kwargs)
        

    def setdefault(self, key, default):
        """  D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D 
        
        **Note** if object is a branch the existence of a key is checked on the branch and the 
        parent version.
            >>> v = VersionnedDict({"x":1})
            >>> v.branch("test").setdefault("x", -99999)
            1

        """
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    if _p2:
        def iteritems(self):
            return VersionItems(self)

        def items(self):
            return list(self.iteritems())

        def iterkeys(self):
            return VersionKeys(self)

        def keys(self):
            return list(self.iterkeys())

        def itervalues(self):
            return VersionValues(self)

        def values(self):
            return list(self.itervalues())

    else:
        def items(self):
            return VersionItems(self)
            
        def keys(self):
            return VersionKeys(self)
            
        def values(self):
            return VersionValues(self)


class RecVersionnedDict(VersionnedDict):
    """ dictionary like object with versioning capabilities 
    
    Unless VersionnedDict, all entries that are a mappable dictionary like object
    is returned as a RecVersion object and get the version/branch/patch of 
    the root RecVersion object. 
    The mappable object is identified if it has the `.keys` method
    
    With RecVerions one can branch a single value of a dictionary 
        
    >>> data = RecVersionnedDict( {1:{'x':10, 'y':100}, 2:{'x':20, 'y':200}} )
    >>> data[1]['x']
    10
    
    >>> other_data = data.branch('other')
    >>> other_data[1] is data[1]
    False
    >>> other_data[1] == data[1]
    True

    >>> other_data[1]['x']  
    10
    >>> other_data[1]['y'] = -100
    >>> other_data[2]['y']
    -100
    >>> data[1]['y']
    100
    >>> data.branch(2.0)[2]['x'] = -10
    >>> data.branch(2.0)[2]['x']
    -10
    """
    def __getitem__(self, item):
        try:
            return self.d[item]
        except KeyError: 
            p = self.parent()
            if p is not None:
                value = p[item]
                if hasattr(value, "keys"):
                    value = RecVersionnedDict(value, self.current_version).branch(self.current_branch)
                    self.d[item] = value
                return value                    
            else:
                raise KeyError('%r'%item)






