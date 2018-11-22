
import unittest
import numpy as np
from PyLBGFS.Tools import ParallelNumpy
from mpi4py import MPI

class test_ParallelNumpy(unittest.TestCase):

    def setUp(self):
        self.np = ParallelNumpy()
        self.comm = MPI.COMM_WORLD
        self.rank  = self.comm.Get_rank()
        self.MPIsize = self.comm.Get_size()
    def test_sum_scalar(self):
        res=self.np.sum(np.array(1))
        self.assertEqual(res, self.np.comm.Get_size())

    def test_sum_1D(self):
        arr=np.array((1,2.1,3))
        res = self.np.sum(arr)
        self.assertEqual(res, self.np.comm.Get_size() * 6.1)

    def test_sum_2D(self):
        arr=np.array(((1,2.1,3),
                     (4,5,6)))
        res = self.np.sum(arr)
        self.assertEqual(res, self.np.comm.Get_size() * 21.1)

    def test_max_2D(self):
        arr=np.reshape(np.array((-1,1,5,4,
                             4,5,4,5,
                             7,0,1,0.),dtype=float),(3,4))

        rank = self.comm.Get_rank()
        if self.comm.Get_size() >=4:
            if rank ==0 :   local_arr = arr[0:2,0:2]
            elif rank ==1 : local_arr = arr[0:2,2:]
            elif rank == 2 :local_arr = arr[2:,0:2]
            elif rank == 3 : local_arr = arr[2:,2:]
            else : local_arr = np.empty(0,dtype=arr.dtype)
        elif self.comm.Get_size() >=2 :
            if   rank ==0 :   local_arr = arr[0:2,:]
            elif rank ==1 : local_arr = arr[2:,:]
            else:           local_arr = np.empty(0, dtype=arr.dtype)
        else:
            local_arr = arr
        self.assertEqual(self.np.max(local_arr),7)

    def test_max_min_empty(self):
        """
        Sometimes the input array is empty
        """
        if self.MPIsize >=2 :
            if self.rank==0:
                local_arr = np.array([], dtype=float)

            else :
                local_arr = np.array([1, 0, 4], dtype=float)
            self.assertEqual(self.np.max(local_arr), 4)
            self.assertEqual(self.np.min(local_arr), 0)

            if self.rank==0:
                local_arr = np.array([1, 0, 4], dtype=float)
            else :

                local_arr = np.array([], dtype=float)
            self.assertEqual(self.np.max(local_arr), 4)
            self.assertEqual(self.np.min(local_arr), 0)

        else :
            local_arr = np.array([],dtype = float)
            #self.assertTrue(np.isnan(self.np.max(local_arr)))
            #self.assertTrue(np.isnan(self.np.min(local_arr)))
            self.assertEqual(self.np.max(local_arr),-np.inf)
            self.assertEqual(self.np.min(local_arr),np.inf)



    def test_min(self):
        arr = np.reshape(np.array((-1, 1, 5, 4,
                                   4, 5, 4, 5,
                                   7, 0, 1, 0),dtype = float), (3, 4))

        rank = self.comm.Get_rank()
        if self.comm.Get_size() >= 4:
            if rank == 0:
                local_arr = arr[0:2, 0:2]
            elif rank == 1:
                local_arr = arr[0:2, 2:]
            elif rank == 2:
                local_arr = arr[2:, 0:2]
            elif rank == 3:
                local_arr = arr[2:, 2:]
            else:
                local_arr = np.empty(0, dtype=arr.dtype)
        elif self.comm.Get_size() >= 2:
            if rank == 0:
                local_arr = arr[0:2, :]
            elif rank == 1:
                local_arr = arr[2:, :]
            else:
                local_arr = np.empty(0, dtype=arr.dtype)
        else:
            local_arr = arr
        self.assertEqual(self.np.min(local_arr), -1)

    def test_dot_row_vectors(self):
        np.random.seed(1)

        n = 10
        fulla = np.random.random(n)
        fullb = np.random.random(n)

        step = n // self.MPIsize

        if self.rank == self.MPIsize - 1:
            loc_sl = slice(self.rank * step, None)
        else:
            loc_sl  = slice(self.rank * step, (self.rank + 1) * step)


        self.assertAlmostEqual(np.asscalar(self.np.dot(fulla[loc_sl],fullb[loc_sl])), np.dot(fulla, fullb),7)


    def test_dot_matrix_vector(self):
        np.random.seed(1)

        m=13
        n = 11

        step = n // self.MPIsize

        if self.rank == self.MPIsize - 1:
            loc_sl = slice(self.rank * step, None)
        else:
            loc_sl = slice(self.rank * step, (self.rank + 1) * step)

        fulla = np.random.random((m,n))
        for fullb in [np.random.random((n,1)),np.random.random(n)]:
            np.testing.assert_allclose(self.np.dot(fulla[:,loc_sl], fullb[loc_sl]), np.dot(fulla, fullb))
            np.testing.assert_allclose(self.np.dot(fullb[loc_sl].T,fulla[:,loc_sl].T),np.dot(fullb.T, fulla.T))
            with self.assertRaises(ValueError):
                self.np.dot(fullb[loc_sl],fulla[:,loc_sl])
            with self.assertRaises(ValueError):
                self.np.dot(fulla[:,loc_sl].T, fullb[loc_sl])

    def test_dot_matrix_matrix(self):
        np.random.seed(1)

        m = 5
        n = 10
        fulla = np.random.random((m, n))
        fullb = np.random.random((n, m))

        step = n // self.MPIsize

        if self.rank == self.MPIsize - 1:
            loc_sl = slice(self.rank * step, None)
        else:
            loc_sl = slice(self.rank * step, (self.rank + 1) * step)

        np.testing.assert_allclose(self.np.dot(fulla[:, loc_sl], fullb[loc_sl,:]), np.dot(fulla, fullb))