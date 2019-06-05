"""
This code give implementation of problems in CSIC 5011 Homework1
Author: CHENG Wei
Affiliation: ECE, HKUST
Contact: wchengad@connect.ust.hk
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import offsetbox
import csv


print(__doc__)
# import sklearn

class PCA:
    def __init__(self, digit):
        # (a) Set up data matrix 
        self.X = self.load_data(digit)

    def load_data(self, digit):
        X = np.zeros((256,0), float)
        with open(digit, "r") as f:
            for l in f.readlines():
                line = l.split(",")
                line = np.asarray(list(map(float, line)))
                X = np.concatenate((X, np.reshape(line, (256, 1))), axis=1)
            return X
    
    def run_pca(self):
        # (b) Compute the mean and centered data matrix
        mu = np.mean(self.X, axis=1, keepdims=True)
        X = self.X - mu
        # (c) Apply SVD on centered data matrix 
        u1, s, vh = np.linalg.svd(X)
        # (d) Compute the covariance matrix and apply eigen decomposition on covariance matrix 
        cov = np.dot(X, np.transpose(X)) / X.shape[1]
        w, u2 = np.linalg.eig(cov)
        # (d) Plot the eigen value curve
        plt.figure()
        ax = plt.subplot(111)
        plt.plot(w / np.sum(w), '.-')
        ax.set_ylabel('eigenvalue')
        ax.set_xlabel('dimension')
        plt.savefig("Eigenvalue_curve",dpi=200)
        plt.close()

        # (e) Visualize the mean and top 24 PCs
        plt.figure()
        plt.subplot(5,5,1)
        plt.xticks([], [])  
        plt.yticks([], [])
        plt.title("0")
        plt.imshow(np.reshape(mu, (16, 16)), cmap=plt.cm.gray_r)
        for i in range(24):
            plt.subplot(5,5,i+2)
            # plt.axis('off')
            plt.xticks([], [])  
            plt.yticks([], [])
            plt.title("%d" % (i+1))
            plt.imshow(np.reshape(u2[:,i], (16, 16)), cmap=plt.cm.gray_r)
        plt.savefig("Sample_mean_and_top_24_PCs",dpi=200)
        plt.close()

        # (f) Sort the image data according to top right singular vectors
        k = 1
        score = np.transpose(vh)[:,0] * np.sqrt(s[0])
        sort = np.argsort(score)
        plt.figure()
        for i in range(25):
            plt.subplot(5,5,i+1)
            # plt.axis('off')
            plt.xticks([], [])  
            plt.yticks([], [])
            plt.imshow(np.reshape(self.X[:,sort[i*24]], (16, 16)), cmap=plt.cm.gray_r)
        plt.savefig("Sort_image_data_via_top_1_left_singular_vector",dpi=200)
        plt.close()

        # (g) Scatter plot image data on top 2 right singular vectors
        k = 2
        embedding = np.transpose(vh)[:,0:k] * np.sqrt(s[0:k])
        plt.figure()
        ax = plt.subplot(1,1,1)
        plt.plot(embedding[:,0], embedding[:,1], '.r')
        ax.set_xlabel('First Principle COmponent')
        ax.set_ylabel('Second Principle COmponent')
        plt.grid(True)
        if hasattr(offsetbox, 'AnnotationBbox'):
            # only print thumbnails with matplotlib > 1.0
            shown_rows = np.array([[1., 1.]])  # just something big
            for i in range(embedding.shape[0]):
                dist = np.sum((embedding[i] - shown_rows) ** 2, 1)
                if np.min(dist) < 2e-2:
                    # don't show points that are too close
                    continue
                shown_rows = np.r_[shown_rows, [embedding[i]]]
                imagebox = offsetbox.AnnotationBbox(
                    offsetbox.OffsetImage(np.reshape(self.X[:,i], (16,16)), cmap=plt.cm.gray_r),
                    embedding[i])
                ax.add_artist(imagebox)
        plt.savefig("Scatter_plot_image_data_on_top 2_right_singular_vectors",dpi=200)
        plt.close()

        # (f) Parallel analysis
        n = 100
        pval = np.zeros(256, float)
        for i in range(n):
            # Get shuffled data matrix within row elements
            Xi = np.zeros((0,X.shape[1]), float)
            for j in range(X.shape[0]):
                Xi = np.concatenate((Xi, np.reshape(np.random.permutation(np.transpose(X[j,:])), (1, -1))), axis=0)
            _, si, _ = np.linalg.svd(Xi)
            pi = np.greater(si, s)
            # pval if permutated eigenvalue is greater than orginal
            pval = pval + pi.astype(float)
        plt.figure()
        ax = plt.subplot(111)
        ax.set_xlabel('dimensions (log scale)')
        ax.set_ylabel('eigenvalue')
        ax.set_yscale('log')
        ax.set_xscale('log')
        plt.plot(s, '.--r', label='original')
        plt.plot(si, '.--b', label='permuted')
        
        ax2 = ax.twinx()
        ax2.set_ylabel('p-values')
        plt.plot(pval/n, 'g', label='p-value')
        ax.legend(loc='lower left')
        ax2.legend(loc='upper right')
        plt.savefig("Parallel_analysis", dpi=200)
        plt.close()

class MDS:
    def __init__(self, dist):
        #load data and construct squared distance matrix
        self.label, self.D = self.load_data(dist)
        self.H = np.eye(self.D.shape[0]) - np.ones(self.D.shape[0]) / self.D.shape[0]
    
    def load_data(self, dist):
        D = []
        with open(dist, newline='') as csvfile:
            rows = csv.reader(csvfile)
            for row in rows:
                D.append(row)
        label = D[0]
        D = np.array(D[1:])
        D[D=='']='0'
        D = D.astype(float)
        D = D + np.transpose(D)
        D = D * D
        return label, D

    def run_mds(self):
        # MDS algorithm
        B = np.dot(np.dot(self.H, self.D), self.H) / -2
        w, v = np.linalg.eig(B)
        
        # Plot normalized eigenvalues
        plt.figure()
        ax = plt.subplot(111)
        plt.plot(w / np.sum(w), '.-')
        ax.set_ylabel('eigenvalue')
        ax.set_xlabel('dimension')
        plt.savefig("MDS_eigenvalue",dpi=200)
        plt.close()

        # Scatter plot of cities using top 2 eigenvectors
        k = 2
        embedding = v[:, 0:k] * np.sqrt(w[0:k])
        plt.figure()
        ax = plt.subplot(1,1,1)
        plt.plot(embedding[:,0], embedding[:,1], 'or')
        ax.set_xlabel('First Principle COmponent')
        ax.set_ylabel('Second Principle COmponent')
        plt.grid(True)
        for i in range(embedding.shape[0]):
            plt.text(embedding[i, 0], embedding[i, 1], self.label[i],
                    color=plt.cm.Set1(i / 10.),
                    fontdict={'weight': 'bold', 'size': 15})
        plt.savefig("2D_scatter_plot_cities",dpi=200)
        plt.close()

if __name__ == '__main__':
    pca = PCA("train.3")
    pca.run_pca()
    mds = MDS("distance.csv")
    mds.run_mds()
