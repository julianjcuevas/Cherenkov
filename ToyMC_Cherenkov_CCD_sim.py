import numpy as np
import matplotlib.pyplot as plt
import math

def isotropic_source(theta_a, theta_b):
    '''
    generates random isotropic azimuthal angle from uniform distribution [0,1]
    and cos^2 theta value which represents the cone for the muon flux incident
    on our CCD at sea level.

    phi goes from [0, 2pi]
    theta goes from [0, pi/2] since this accounts for the lower regime of emitted
    particles and the other half will not be incident on the CCD
    '''
    r1 = np.random.uniform(0,1)
    phi = 2*np.pi*r1

    r2 = np.random.uniform(0,1)
    cos_sq_th = math.cos(theta_a)**2 + r2*(math.cos(theta_b)**2 - math.cos(theta_a)**2)

    theta = math.acos(math.sqrt(cos_sq_th))

    return phi, cos_sq_th, theta


#def cosmic_ray_flux():


#plot histogram to check for flat line along degrees

N = 100000

angle = []
cone = []
zenith = []

for n in range(N):
    phi, cos_sq_th, theta = isotropic_source(0, math.pi/2)
    angle.append(phi)
    cone.append(cos_sq_th)
    zenith.append(theta)

n_bins = 40

plt.hist(angle, bins = n_bins, color = '#377eb8', edgecolor = 'k')
plt.xlabel("Angular Distribution")
plt.ylabel("Counts")
plt.title("Angular Distribution of Isotropic Source")
plt.show()

plt.hist(cone, bins = n_bins, color = '#377eb8', edgecolor = 'k')
plt.xlabel("Angular Distribution")
plt.ylabel("Counts")
plt.title(r"$\cos^2{\theta}$ Distribution of Isotropic Source")
plt.show()

plt.hist(zenith, bins = n_bins, color = '#377eb8', edgecolor = 'k')
plt.xlabel("Angular Distribution")
plt.ylabel("Counts")
plt.title(r"$\theta$ Distribution of Isotropic Source")
plt.show()
