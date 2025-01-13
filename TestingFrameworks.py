import unittest
import numpy as np
from numpy.testing import assert_allclose, assert_array_almost_equal
import pytest
from typing import Dict, Tuple

# Base Test Class for Physics
class PhysicsTest:
    """Base class for physics tests with common utilities"""
    
    @staticmethod
    def check_conservation(initial: np.ndarray, final: np.ndarray, 
                         tolerance: float = 1e-10) -> bool:
        """Check conservation laws"""
        return np.all(np.abs(initial - final) < tolerance)
    
    @staticmethod
    def check_unitarity(S_matrix: np.ndarray, 
                       tolerance: float = 1e-10) -> bool:
        """Check unitarity of S-matrix"""
        identity = np.eye(S_matrix.shape[0])
        return np.all(np.abs(S_matrix @ S_matrix.conj().T - identity) < tolerance)
    
    @staticmethod
    def check_gauge_invariance(observable: float, 
                             gauge_transform: callable,
                             tolerance: float = 1e-10) -> bool:
        """Check gauge invariance of observables"""
        return abs(observable - gauge_transform(observable)) < tolerance

# Scalar Field Tests
class TestScalarField(unittest.TestCase, PhysicsTest):
    """Test suite for scalar field theory"""
    
    def setUp(self):
        """Initialize test parameters"""
        self.mass = 1.0
        self.coupling = 0.1
        self.momentum = np.array([1.0, 0.0, 0.0, 0.0])
    
    def test_klein_gordon(self):
        """Test Klein-Gordon equation"""
        from scalar_field.core.classical import klein_gordon
        
        # Test on-shell condition
        p2 = np.sum(self.momentum**2)
        assert_allclose(p2 - self.mass**2, 0, rtol=1e-10,
                       err_msg="Klein-Gordon equation not satisfied")
    
    def test_propagator(self):
        """Test scalar propagator"""
        from scalar_field.core.quantum import propagator
        
        prop = propagator(self.momentum, self.mass)
        expected = 1j/(self.momentum@self.momentum - self.mass**2 + 1e-10j)
        assert_allclose(prop, expected, rtol=1e-10,
                       err_msg="Incorrect propagator")
    
    def test_phi4_vertex(self):
        """Test φ⁴ interaction"""
        from scalar_field.interactions.vertices import phi4
        
        vertex = phi4(self.coupling)
        expected = -1j * self.coupling
        assert_allclose(vertex, expected, rtol=1e-10,
                       err_msg="Incorrect φ⁴ vertex")

# QCD Tests
class TestQCD(unittest.TestCase, PhysicsTest):
    """Test suite for QCD"""
    
    def setUp(self):
        """Initialize QCD parameters"""
        self.Nc = 3  # Number of colors
        self.g = 1.0  # Coupling constant
        self.generators = self._init_generators()
    
    def _init_generators(self):
        """Initialize SU(3) generators"""
        # Simplified Gell-Mann matrices
        return np.array([[[0, 1, 0], [1, 0, 0], [0, 0, 0]]])
    
    @pytest.mark.slow
    def test_gauge_invariance(self):
        """Test gauge invariance of QCD"""
        from qcd.core.gauge_sector import field_strength
        
        # Random gauge field
        A_mu = np.random.rand(4, 3, 3)
        F_munu = field_strength(A_mu, self.generators)
        
        def gauge_transform(alpha):
            U = np.exp(1j * alpha * self.generators[0])
            return U @ F_munu @ U.conj().T
        
        # Check gauge invariance
        alpha = np.random.rand()
        assert self.check_gauge_invariance(
            np.trace(F_munu @ F_munu),
            lambda x: np.trace(gauge_transform(alpha) @ gauge_transform(alpha)),
            tolerance=1e-8
        )
    
    def test_casimir_operators(self):
        """Test Casimir operators"""
        from qcd.symmetries.gauge import casimir
        
        # Test quadratic Casimir for fundamental representation
        C2_fund = casimir.quadratic_fundamental(self.Nc)
        expected = (self.Nc**2 - 1)/(2*self.Nc)
        assert_allclose(C2_fund, expected, rtol=1e-10,
                       err_msg="Incorrect fundamental Casimir")

# QED Tests
class TestQED(unittest.TestCase, PhysicsTest):
    """Test suite for QED"""
    
    def setUp(self):
        """Initialize QED parameters"""
        self.alpha = 1/137.036
        self.mass_electron = 0.511  # MeV
    
    def test_ward_identity(self):
        """Test Ward identity"""
        from qed.radiative_corrections.vertex import ward_identity
        
        q = np.array([1.0, 0.0, 0.0, 0.0])
        p = np.array([2.0, 1.0, 0.0, 0.0])
        
        # Vertex function
        Gamma = ward_identity.vertex_function(q, p, self.mass_electron)
        
        # Self energy difference
        dSigma = ward_identity.self_energy_difference(q, p, self.mass_electron)
        
        # Check Ward identity
        assert_allclose(q @ Gamma, dSigma, rtol=1e-8,
                       err_msg="Ward identity violated")
    
    def test_cross_section(self):
        """Test QED cross sections"""
        from qed.interactions.processes import compton
        
        # Test Compton scattering
        E = 1.0  # GeV
        theta = np.pi/4
        sigma = compton.differential_cross_section(E, theta)
        
        # Check positivity and finiteness
        assert sigma > 0, "Negative cross section"
        assert np.isfinite(sigma), "Infinite cross section"

# Gravity Tests
class TestGravity(unittest.TestCase, PhysicsTest):
    """Test suite for gravity"""
    
    def setUp(self):
        """Initialize gravitational parameters"""
        self.G = 6.674e-11
        self.c = 299792458
    
    def test_bianchi_identity(self):
        """Test Bianchi identity"""
        from gravity.core.geometry import curvature
        
        # Test metric (Schwarzschild)
        def metric(r):
            f = 1 - 2*self.G*1.0/(r*self.c**2)
            return np.diag([f, -1/f, -r**2, -r**2*np.sin(0.1)**2])
        
        r = 10.0  # Test radius
        R = curvature.riemann_tensor(metric(r))
        
        # Check cyclic identity
        cyclic_sum = (R[0,1,2,3] + R[0,2,3,1] + R[0,3,1,2])
        assert_allclose(cyclic_sum, 0, atol=1e-8,
                       err_msg="Bianchi identity violated")
    
    def test_schwarzschild(self):
        """Test Schwarzschild solution"""
        from gravity.classical_solutions.vacuum import schwarzschild
        
        M = 1.0  # Solar masses
        r = 100.0  # km
        
        # Test horizon
        r_h = schwarzschild.horizon_radius(M)
        expected_r_h = 2*self.G*M/self.c**2
        assert_allclose(r_h, expected_r_h, rtol=1e-10,
                       err_msg="Incorrect horizon radius")

if __name__ == '__main__':
    unittest.main()
