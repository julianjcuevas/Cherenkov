import numpy as np
from scipy import integrate
from scipy import interpolate
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
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
    cos_sq_th = np.cos(theta_a)**4 + r2*(np.cos(theta_b)**4 - np.cos(theta_a)**4)

    theta = np.arccos(np.power(cos_sq_th, 1/4))

    return phi, theta


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
    '''
    This function calculates the number of cherenkov photons generated by an
    incident charged particle, and the cherenkov angle distribution by wavelength.
    (each value of n coincides with a specific wavelength).

    the function takes in an energy E in eV
    wavelength in meters
    index of refraction n
    extinction coefficient k
    and ccd thickness z in meters
    '''
    alpha = 1/137.
    m = 106E6 #muon mass eV/c
    B = math.sqrt((E**2 - m**2))/E

    const = 2*np.pi*alpha*z #need to update this later with code for angle of incidence
    denom = (n+1j*k)**2 * (B**2)
    dN = const*(1-(1/(denom)))/(wavelength**2)

    N = integrate.simps(dN, wavelength)

    ch_angle = np.arccos(1/(B*(n+1j*k)))*(180/np.pi)

    return int(N.real), ch_angle.real, B

def cherenkov_photon_properties(x_p, y_p, h, theta, phi, lam_0, lam_1):
    '''
    This function generates a position along the path of muon for generation
    of a cherenkov photon and determines its associated wavelength
    '''
    r = np.random.uniform()

    x = x_p - r*h*np.tan(theta)*np.cos(phi)
    y = y_p - r*h*np.tan(theta)*np.sin(phi)
    z = h - r*(h/np.cos(theta))

    lamda = lam_0/(1 - r*(1-lam_0/lam_1))

    return x, y, z, lamda


def absorption_dist_cherenkov(abs, wavelength, lam, theta, phi):
    '''
    Determines the point of absorption for a cherenkov photon of a given wavelength
    in the muon frame (ie the z_prime axis coincides with the muon path)

    In this calculation we have the photon being generated in the origin of the
    primed axis, thus values we generate are merely the displacement from the origin

    once we transform to the ccd frame we determine the cherenkov photon absorption
    position in the ccd
    '''
    print("lam: " + str(lam))
    depth = interpolate.interp1d(wavelength, abs, kind = 'linear')
    print("depth" + str(depth(lam*1E9)))

    abs_length = -(1/depth(lam*1E9))*np.log(np.random.uniform(0,1))

    print("abs length m: " + str(abs_length))

    x_dis = abs_length*np.sin(theta)*np.cos(phi)
    print(x_dis)
    y_dis = abs_length*np.sin(theta)*np.sin(phi)
    z_dis = abs_length*np.cos(theta)

    return x_dis, y_dis, z_dis

def rotation_onto_ccd_frame(ch_theta, ch_phi, theta, phi):
    '''
    uses the ch photon direction( theta and phi ) in respect to the muon frame and the muon's direction
    (theta and phi) in respect to the ccd frame to determine the ch photon direction in respect
    to the ccd frame (theta and phi)
    '''

    T_gamma = theta + ch_theta*np.cos(ch_phi) #determines theta in respect to ccd
    P_gamma = phi + ch_theta*np.sin(ch_phi) #determines phi in respect to the ccd

    return T_gamma, P_gamma

def dot_product(x_mu, y_mu, z_mu, x_ch, y_ch, z_ch, x_abs, y_abs, z_abs):

    '''uses dot product to make sure we return the cherenkov angle
        between muon vector and ch photon vector '''

    dot = (x_ch-x_mu)*(x_abs-x_ch) + (y_ch-y_mu)*(y_abs-y_ch) + (z_ch-z_mu)*(z_abs-z_ch)
    mu_mag = np.sqrt((x_ch-x_mu)**2 + (y_ch-y_mu)**2 + (z_ch-z_mu)**2)
    abs_mag = np.sqrt((x_abs-x_ch)**2 + (y_abs-y_ch)**2 + (z_abs-z_ch)**2)

    angle = np.arccos((dot/(mu_mag*abs_mag)))

    return angle

def critical_angle(wavelength, n, k, theta_gamma, lam):
    '''
    Given a cherenkov photon of wavelength lambda, this function calculates the
    associated critical angle for a photon exiting the ccd into vacuum (n =1)
    '''
    modulus = np.abs(n + 1j*k) #calculates modulus of index of refraction
    print(modulus)
    index = interpolate.interp1d(wavelength, modulus, kind = 'linear')
    crit_angle = np.arcsin(1/index(lam*1E9))

    return crit_angle


def plot_check():
    #plot histogram to check for flat line along degrees

    N = 100000


    angle = []
    #cone = []
    zenith = []

    for n in range(N):
        phi, theta = isotropic_source(0, math.pi/2)
        angle.append(phi)
        #cone.append(cos_sq_th)
        zenith.append(theta*(180/np.pi))

    n_bins = 40

    plt.hist(angle, bins = n_bins, color = '#377eb8', edgecolor = 'k')
    plt.xlabel("Angular Distribution")
    plt.ylabel("Counts")
    plt.title(r"$\phi$ Distribution of Isotropic Source")
    plt.show()

    plt.hist(zenith, bins = n_bins, color = '#377eb8', edgecolor = 'k')
    plt.xlabel("Angular Distribution")
    plt.ylabel("Counts")
    plt.title(r"$\theta$ Distribution of Isotropic Source")
    plt.show()



def ccd_plot(X_ccd, Y_ccd, Z_ccd, x_mu, y_mu, z_mu, x_abs, y_abs, z_abs, status_ch):
    '''This function will plot the trajectories of the muons and ch photons in
    the ccd'''
    x_ccd = np.linspace(-X_ccd/2, X_ccd/2, num=100)
    y_ccd = np.linspace(-Y_ccd/2, Y_ccd/2, num=100)
    z_ccd = np.linspace(0, Z_ccd, num=100)

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.plot(x_ccd, np.repeat(Y_ccd/2,len(x_ccd)), np.zeros(len(x_ccd)), color='black')
    ax.plot(x_ccd, np.repeat(-Y_ccd/2,len(x_ccd)), np.zeros(len(x_ccd)), color='black')
    ax.plot(np.repeat(X_ccd/2,len(y_ccd)),y_ccd, np.zeros(len(y_ccd)), color='black')
    ax.plot(np.repeat(-X_ccd/2,len(y_ccd)),y_ccd, np.zeros(len(y_ccd)), color='black')

    ax.plot(x_ccd, np.repeat(Y_ccd/2,len(x_ccd)), np.repeat(Z_ccd,len(x_ccd)), color='black')
    ax.plot(x_ccd, np.repeat(-Y_ccd/2,len(x_ccd)), np.repeat(Z_ccd,len(x_ccd)), color='black')
    ax.plot(np.repeat(X_ccd/2,len(y_ccd)),y_ccd, np.repeat(Z_ccd,len(y_ccd)), color='black')
    ax.plot(np.repeat(-X_ccd/2,len(y_ccd)),y_ccd, np.repeat(Z_ccd,len(y_ccd)), color='black')

    ax.plot(np.repeat(X_ccd/2,len(x_ccd)), np.repeat(Y_ccd/2,len(x_ccd)), z_ccd, color='black')
    ax.plot(np.repeat(-X_ccd/2,len(x_ccd)), np.repeat(Y_ccd/2,len(x_ccd)), z_ccd, color='black')
    ax.plot(np.repeat(X_ccd/2,len(x_ccd)), np.repeat(-Y_ccd/2,len(x_ccd)), z_ccd, color='black')
    ax.plot(np.repeat(-X_ccd/2,len(x_ccd)), np.repeat(-Y_ccd/2,len(x_ccd)), z_ccd, color='black')

    ax.scatter(x_mu, y_mu, z_mu, color='red')
    ax.scatter(x_abs, y_abs, z_abs, color='blue')
    plt.show()




'''
    plt.hist(cone, bins = n_bins, color = '#377eb8', edgecolor = 'k')
    plt.xlabel("Angular Distribution")
    plt.ylabel("Counts")
    plt.title(r"$\cos^4{\theta}$ Distribution of Isotropic Source")
    plt.show()
'''


#plot_check()



X_ccd = 9E-2 #m
Y_ccd = 1.5E-2 #m
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
X_p2 = [] #muon exit position
Y_p2 = []

X_ch_ph = [] #the origin x pos of ch. photon i of given energy
Y_ch_ph = [] #the origin y pos of ch. photon i  of given energy
Z_ch_ph = [] #the origin z pos of ch. photon i of giveb energy
lam_ch_ph = [] #the wavelength of ch. photon i
status_ch = [] #boolean value of whether the photon was absorbed or escaped
X_ch_abs = [] #absorption x pos of photon i
Y_ch_abs = [] #absorpiton y pos of photon i
Z_ch_abs = [] #absorption z pos of photon i
Ch_ID = [] #id for given photons per muon
Ch_num_per_muon = []

h = 4.13567E-15  # planck's const in eV/Hz
c = 3E8  # speed of light in vacuum m/s

events = 100


for p in range(events):
    x_p, y_p = muon_incident_on_CCD(X_ccd, Y_ccd)
    phi, theta = isotropic_source(th_1, th_2) #radians
    X_p.append(x_p)
    Y_p.append(y_p)
    Phi_p.append(phi)
    Theta_p.append(theta)

    muon_path = ccd_thickness/(np.cos(theta)) #calculates the muon path length in ccd

    X_p2.append(x_p - ccd_thickness*np.tan(theta)*np.cos(phi))
    Y_p2.append(y_p - ccd_thickness*np.tan(theta)*np.sin(phi))


    ch_ph_num, ch_angle, beta = cherenkov_photons(E_muon, wavelength*1E-9, n, k, muon_path)
    Ch_num_per_muon.append(ch_ph_num)
    Ch = interpolate.interp1d(wavelength, ch_angle, kind = 'linear')
    #determines the cherenkov angle as a function of wavelength
    #print(ch_ph_num)
    for photon in range(ch_ph_num):
        x_ch, y_ch, z_ch, lam = cherenkov_photon_properties(x_p, y_p, ccd_thickness, theta, phi, 400E-9, 1000E-9)
        #print(lam)
        X_ch_ph.append(x_ch)
        Y_ch_ph.append(y_ch)
        Z_ch_ph.append(z_ch)
        lam_ch_ph.append(lam*1E9)
        Ch_ID.append(photon)

        Ch_angle = Ch(lam*1E9)*(np.pi/180) #radians
        print(str(Ch_angle*180/np.pi) + ' ' + str(lam*1E9))
        #ch_rel_z = Ch_angle + theta #determine ch photon i angle relative to z in radians
        # here z coincides with the z axis of the ccd
        ch_phi = np.random.uniform(0,1)*2*np.pi #generates the phi angle rel to muon

        #code below determines the distance away from muon where ch photon is abs in ccd frame
        theta_gamma, phi_gamma = rotation_onto_ccd_frame(Ch_angle, ch_phi, theta, phi) #radians

        x_dis, y_dis, z_dis = absorption_dist_cherenkov(abs_depth, wavelength, lam,
            theta_gamma, phi_gamma)

        x_ch_abs = x_ch - x_dis #x coordinate in ccd* where photon is absorbed
        y_ch_abs = y_ch - y_dis #y coordinate in ccd* where photon is absorbed
        z_ch_abs = z_ch - z_dis #z coordinate in ccd* where photon is absorbed

        X_ch_abs.append(x_ch_abs)
        Y_ch_abs.append(y_ch_abs)

        if z_ch_abs < 0:
            crit = critical_angle(wavelength, n, k, theta_gamma, lam)
            if theta_gamma < crit:
                status_ch.append(0)  # the photon exited the ccd without absorption
                Z_ch_abs.append(z_ch_abs)
            elif theta_gamma > crit:
                status_ch.append(1)
                Z_ch_abs.append(0-z_ch_abs) # due to reflection, this should result in the photon being at the same x, y position but the remaining z distance above 0
            else:
                status_ch.append(1) #the photon was either internally reflected or "rode" the boundary and was absorbed
                Z_ch_abs.append(z_ch_abs)
        else:
            status_ch.append(1) #the photon was absorbed in ccd
            Z_ch_abs.append(z_ch_abs)

        #t = dot_product(x_ch, y_ch, z_ch, x_dis_ccd, y_dis_ccd, z_dis_ccd)
        t = dot_product(x_p, y_p, 0, x_ch, y_ch, z_ch, x_ch_abs, y_ch_abs, z_ch_abs)
        print(str(t*180/np.pi))


plt.scatter(wavelength, np.log(abs_depth))
plt.show()

plt.hist(lam_ch_ph, bins = 40, color = '#377eb8', edgecolor = 'k')
plt.xlabel(r'$\lambda$ (nm)')
plt.ylabel("Counts")
plt.title("Wavelength Distribution of Cherenkov Photons")
plt.show()

plt.hist(Ch_num_per_muon, color = '#377eb8', edgecolor = 'k')
plt.xlabel('number of Cherenkov Photons generated')
plt.ylabel("Counts")
plt.title("Distribution of Cherenkov Photons Per Muon")
plt.show()

plt.hist(status_ch,color = '#377eb8', edgecolor = 'k')
plt.xlabel('0 if not absorbed, 1 if absorbed')
plt.ylabel('Counts')
plt.title('Status of Ch. Photon in CCD')
plt.show()


ccd_plot(X_ccd, Y_ccd, ccd_thickness, X_p, Y_p, np.repeat(ccd_thickness, len(X_p)),
        X_ch_abs, Y_ch_abs, Z_ch_abs, status_ch)
print(cherenkov_photons(E_muon, wavelength*1E-9, n, k, ccd_thickness))
print(status_ch)

print("muon:" + str(X_p[:10]))
print("photon x:" + str(X_ch_abs[:10]))
print("photon z:" + str(Z_ch_abs[:25]))
#plt.scatter(wavelength, n)
#plt.scatter(wavelength, k)
#plt.plot(wavelength, abs_depth, marker = 'o')
#plt.plot(wavelength, a, marker = 'o')
#plt.yscale('log')
#plt.show()
