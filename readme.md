# What is it ? 

This package redefine a dictionary object. On top of storing data, these dictionaries can have different versions, branches or patches.

It is mostly useful for development or data analysis also for package configuration.

# How it works ?

A `Versions` object get all the dictionary methods. But on top the dictionary can have several versions, each versions can have branches, each branches can have version or sub-branches. On top of it the object can be patched, patch is applied on top of versions.

The main difference between version and branch is that versions are completely independent from one to an other, they are structured at the same level. Meaning that one can jump from one version to other from any version.
Branches are structured hierarchically, a returned branch is the child of its parent. Items not defined in the branch are taken from the parent.

### Version example

        filter = Versions({"x": [1, 2, 3, 4, 5],
                         "y": [0, 0, 0, 0, 0], 
                         "description": "Blocked filter"
                         }, 
                        version="blocked"
                        )
        filter.version("door").update({
            "x": [1, 2, 3, 4, 5],
            "y": [0, 1, 1, 1, 0], 
            "description": "Door filter"
        })
        filter.version("dirack").update({
            "x": [1,   2,   3,   4,   5],
            "y": [0.0, 0.0, 1, 0.0  0.0], 
            "description": "Dirack filter"
        })
        filter.version("triangle").update({
            "x": [1,   2,   3,   4,   5  ],
            "y": [0.0, 0.5  1,   0.5  0.0], 
           "description": "Triangle filter" 
        })

different version can be retrieved as a new object or one can change the version in-place, which is a most obvious advantage of version compare to just structured dictionary.

        >>> filter.version('triangle')['description']
        "Triangle filter" 
        >>> filter['description']
        "blocked filter"
        >>> filter.change_version('triangle')
        >>> filter['description']
        "Triangle filter"        

From any version one can jump to an other 

    >>> filter.version('triangle').version('dirack')['description']
    "Dirack filter"


### Branch example

Following the previous example this is clear that the 'x' item is always the same. Instead of creating a version for each 'filter' on can create branch and change only the changing part.

        filter = Versions({"x": [1, 2, 3, 4, 5],
                           "y": [0, 0, 0, 0, 0], 
                           "description": "Blocked filter"
                         }, 
                        version="blocked"
                        )
        filter.branch("door").update({            
            "y": [0, 1, 1, 1, 0], 
            "description": "Door filter"
        })
        filter.branch("dirack").update({            
            "y": [0.0, 0.0, 1, 0.0  0.0], 
            "description": "Dirack filter"
        })
        filter.branch("triangle").update({
            "y": [0.0, 0.5  1,   0.5  0.0], 
           "description": "Triangle filter" 
        })


        >>> filter.branch("triangle")["x"]
        [1, 2, 3, 4, 5]
        >>> filter.branch("triangle")["y"]
        [0.0, 0.5  1,   0.5  0.0]


The main draw back of this is that `filter.branch('door')['x'][2] = 0` will affect the `filter['x']` object because `filter.branch('door')['x'] is filter['x']`










