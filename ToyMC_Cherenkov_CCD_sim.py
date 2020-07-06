import numpy as np
import matplotlib.pyplot as plt

def isotropic_source():
    '''
    generates random isotropic azimuthal angle from uniform distribution [0,1]

    '''
    r = np.random.uniform(0,1)
    phi = 2*np.pi*r

    return phi


def cosmic_ray_flux():

#plot histogram to check for flat line along degrees

N = 100000

angle = []

for n in range(N):
    phi = isotropic_source()
    angle.append(phi)

n_bins = 40

plt.hist(angle, bins = n_bins, color = '#377eb8', edgecolor = 'k')
plt.xlabel("Angular Distribution")
plt.ylabel("Counts")
plt.title("Angular Distribution of Isotropic Source")
plt.show()
