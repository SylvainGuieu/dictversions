#!/usr/bin/env python
import unittest
from dictversions import *

class TestVersions(unittest.TestCase):

    def test_branch(self):
        v = VersionnedDict({})
        v['a'] = 'root a'
        v.branch(2.0)['b'] = '2.0 b'

        self.assertEqual(v['a'], 'root a')
        self.assertEqual(v.branch(2.0)['a'], 'root a')
        self.assertEqual(v.branch(2.0)['b'], '2.0 b')        

        with self.assertRaises(KeyError):
          v['b']

        self.assertEqual('a' in v.branch(2.0), True)        
        v.branch(2.0, a='2.0 a')
        self.assertEqual(v.branch(2.0)['a'], '2.0 a')

    def test_iter(self):
        v = VersionnedDict({})
        v['a'] = 'root a'
        v.branch(2.0)['b'] = '2.0 b'

        self.assertEqual(sorted(v.branch(2.0)), sorted(['b','a']))
        
        self.assertEqual(sorted(v.items()), sorted([ ('a','root a')])   )
        self.assertEqual(sorted(v.branch(2.0).items()), sorted([('b','2.0 b'), ('a','root a')])   )
        self.assertEqual(sorted(v.branch(2.0).values()), sorted(['2.0 b','root a']))

        v.branch(2.0)['a'] = '2.0 a'
        self.assertEqual(sorted(v.branch(2.0)), sorted(['a','b']))
        self.assertEqual(sorted(v.branch(2.0).values()), sorted(['2.0 a','2.0 b']))

    def test_version(self):
        v1 = VersionnedDict({"x":1, "y":10}, version=1)
        v2 = v1.version(2, **v1)
        v2['x'] *= 2
        self.assertEqual(v1['x'],1)
        self.assertEqual(v2['x'],2)
        v2['color'] = "red"
        self.assertEqual(v2['color'],'red')
        with self.assertRaises(KeyError):
          v1['color']

    def test_version2(self):
        v = VersionnedDict({}, version=1)
        v.version(1).update( x=10, y=20)
        v.version(2).update( x=10, y=40)
        self.assertEqual( v.version(2)['y'], 40)

    def test_rec(self):
        v = RecVersionnedDict({})
        v[1] = {'x':1, 'y':10}
        v[2] = {'x':2, 'y':20}
        self.assertEqual(v[1]['x'], 1)
        self.assertEqual(v.branch('toto')[1]['x'], 1)
        toto = v.branch("toto")
        toto[1]['x'] = 99
        self.assertEqual(v.branch('toto')[1]['x'], 99)
        self.assertEqual(v[1]['x'], 1)

    def test_rec2(self):
        v = RecVersionnedDict({})

        v.update({
            1: {"a": {'x':"1ax", 'y':"1ay"}, 
                "b": {'x':"1bx", 'y':"1by"},
                "c": {'x':"1cx", 'y':"1cy"}
                },
            2: {"a": {'x':"2ax", 'y':"2ay"}, 
                "b": {'x':"2bx", 'y':"2by"},
                "c": {'x':"2cx", 'y':"2cy"}
                }
            }
        )
        b = v.branch("|")

        b[1]["a"]["x"] = "|"+v[1]["a"]["x"]+"|"


        self.assertEqual(b[1]["a"]["x"], "|1ax|" )
        self.assertEqual(v[1]["a"]["x"], "1ax" )

        b[2]["b"] = {"x":0, "y":0}
        self.assertEqual(b[2]["b"]["x"], 0)
        b.branch(1)[2]["b"]["x"] = 99
        self.assertEqual(b.branch(1)[2]["b"]["x"], 99)


        
    def test_patch(self):
        v = VersionnedDict({}, version=1)
        v.version(1).update( x=10, y=20)
        v.version(2).update( x=10, y=40)
        v.patch('p').update(x=2)

        self.assertEqual( v.version(1).patch('p')['x'], 2)
        self.assertEqual( v.version(2).patch('p')['x'], 2)
        self.assertEqual( v.version(1).patch('p')['y'], 20)
        self.assertEqual( v.version(2).patch('p')['y'], 40)

        p = v.patch('p')
        self.assertEqual( p['y'], 20)
        self.assertEqual( p.version(2)['y'], 40)
        p.version(2)['y'] = 99
        self.assertEqual( p.version(2)['y'], 99)
        self.assertEqual( p.version(1)['y'], 99)
        self.assertEqual( v.version(1)['y'], 20)



if __name__ == '__main__':
    unittest.main()

