import numpy as np
from scipy import integrate
import matplotlib.pyplot as plt
import math

plt.set_cmap('viridis')

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


def muon_incident_on_CCD(X_ccd, Y_ccd):
    '''
    Generate the incident muons coordinates on the CCD
    '''

    x = -(X_ccd/2) + np.random.uniform(0,1)*X_ccd
    #the division by 2 implies the coordinate axis is centered around the ccd center
    y = -(Y_ccd/2) + np.random.uniform(0,1)*Y_ccd

    return x, y

def muon_flux(I_0, A_0, th_1, th_2):
    '''
    takes in theta values for solid angles between [0, pi/2] and
    integrates to determine flux at given theta range.

    outputs int since it doesnt make sense to have a partial muon
    '''
    theta = np.linspace(th_1, th_2, num = 70)
    dflux = I_0*2*np.pi*A_0*(np.cos(theta)**3)*np.sin(theta)
    flux = integrate.simps(dflux, theta)

    return int(flux)

def cherenkov_photons(E, wavelength, n, k, z):
    alpha = 1/137.
    m = 106E6 #muon mass eV/c
    B = math.sqrt((E**2 - m**2))/E

    const = 2*np.pi*alpha*z
    denom = (n+1j*k)**2 * (B**2)
    dN = const*(1-(1/(denom)))/(wavelength**2)

    N = integrate.simps(dN, wavelength)

    ch_angle = np.arccos(1/(B*(n+1j*k)))*(180/np.pi)
    return int(N.real), ch_angle.real




def plot_check():
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

#plot_check()



X_ccd = 9 #cm
Y_ccd = 1.5 #cm
ccd_thickness = 675E-6 #meters

I_0 = 1 #muon flux at theta = 0 per cm^2 per min
E_muon = 4E9 #eV

Si_optic_properities = np.loadtxt('/Users/Julian/github/Cherenkov/silicon_optical_properties.txt',
    delimiter = '\t', skiprows = 15, max_rows = (76-15))

'''
I choose to truncate file reading at 76th row since there is missing data for 2 columns after this point.
This should not cause problems in the physics since row 76 coincides with
1000 nm wavelength which is the upper limit to silicons absorption spectra
'''

wavelength = Si_optic_properities[:,0] #wavelength in nanometers
a = Si_optic_properities[:,1] #absorption coefficient per cm
abs_depth = Si_optic_properities[:,2] #absorption depth (m)
n = Si_optic_properities[:,3] #index of refraction at specified wavelength
k = Si_optic_properities[:,4] #extinction coefficient
ref_coef = Si_optic_properities [:, 5] #reflection

th_1 = 0
th_2 = np.pi/2
flux = muon_flux(I_0, (X_ccd*Y_ccd), th_1, th_2)

X_p = [] #muon i x-coordinate
Y_p = [] #muon i y-coordinate
Phi_p = [] #muon i azimuthal angle of incidence
Theta_p = [] #muon i zenith angle of incidence

# i use the muon flux to determine the number of muons incident in ccd per dt
for p in range(flux):
    x_p, y_p = muon_incident_on_CCD(X_ccd, Y_ccd)
    phi, cos_sq, theta = isotropic_source(th_1, th_2)
    X_p.append(x_p)
    Y_p.append(y_p)
    Phi_p.append(phi)
    Theta_p.append(theta)

print(cherenkov_photons(E_muon, wavelength*1E-9, n, k, ccd_thickness))
#plt.scatter(wavelength, n)
#plt.scatter(wavelength, k)
#plt.plot(wavelength, abs_depth, marker = 'o')
#plt.plot(wavelength, a, marker = 'o')
#plt.yscale('log')
#plt.show()
