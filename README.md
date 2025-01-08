# PythonNote


## Python Proof Class

```python
from typing import List, Dict, Set, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import math

class ProofType(Enum): 
    """Types of mathematical proofs"""
    DIRECT = "direct"
    CONTRADICTION = "contradiction"
    INDUCTION = "induction"
    CONTRAPOSITIVE = "contrapositive"

@dataclass
class Statement:
    """Mathematical statement or proposition"""
    content: str
    is_premise: bool = False
    is_conclusion: bool = False
    justification: Optional[str] = None

class ProofStep:
    """Single step in a proof"""
    def __init__(self, statement: str, reason: str, references: List[int] = None):
        self.statement = statement
        self.reason = reason
        self.references = references or []
    
    def __str__(self) -> str:
        ref_str = f" (from steps {', '.join(map(str, self.references))})" if self.references else ""
        return f"{self.statement} [{self.reason}]{ref_str}"

class MathematicalProof:
    """Framework for constructing and verifying mathematical proofs"""
    
    def __init__(self, proof_type: ProofType):
        self.type = proof_type
        self.steps: List[ProofStep] = []
        self.premises: Set[str] = set()
        self.conclusion: Optional[str] = None
        self.assumptions: Set[str] = set()
        
    def add_premise(self, statement: str) -> None:
        """Add premise to proof"""
        self.premises.add(statement)
        self.steps.append(ProofStep(statement, "Given premise"))
    
    def add_assumption(self, statement: str) -> None:
        """Add assumption for contradiction/contrapositive"""
        self.assumptions.add(statement)
        self.steps.append(ProofStep(statement, "Assumption"))
    
    def add_step(self, statement: str, reason: str, 
                references: List[int] = None) -> None:
        """Add proof step with justification"""
        self.steps.append(ProofStep(statement, reason, references))
    
    def set_conclusion(self, statement: str) -> None:
        """Set proof conclusion"""
        self.conclusion = statement
    
    def verify(self) -> bool:
        """Verify proof structure and logic"""
        if not self.steps:
            return False
            
        if not self.conclusion:
            return False
            
        # Verify references
        for step in self.steps:
            if step.references:
                if not all(0 <= ref < len(self.steps) for ref in step.references):
                    return False
        
        # Verify proof type specific rules
        if self.type == ProofType.CONTRADICTION:
            # Must have assumption and reach contradiction
            if not self.assumptions:
                return False
            if not any("contradiction" in step.statement.lower() 
                      for step in self.steps):
                return False
                
        elif self.type == ProofType.INDUCTION:
            # Must have base case and inductive step
            has_base = False
            has_inductive = False
            for step in self.steps:
                if "base case" in step.reason.lower():
                    has_base = True
                if "inductive step" in step.reason.lower():
                    has_inductive = True
            if not (has_base and has_inductive):
                return False
        
        return True
    
    def display(self) -> None:
        """Display formatted proof"""
        print(f"\nProof by {self.type.value}:")
        print("Premises:", ", ".join(self.premises))
        if self.assumptions:
            print("Assumptions:", ", ".join(self.assumptions))
        print("\nSteps:")
        for i, step in enumerate(self.steps):
            print(f"{i+1}. {step}")
        print("\nConclusion:", self.conclusion)

class InductionProof(MathematicalProof):
    """Specialized class for inductive proofs"""
    
    def __init__(self, base_case: int = 1):
        super().__init__(ProofType.INDUCTION)
        self.base_case = base_case
        self.inductive_var = 'n'
    
    def add_base_case(self, statement: str, verification: Callable[[int], bool]) -> None:
        """Add and verify base case"""
        result = verification(self.base_case)
        self.add_step(
            f"Base case (n={self.base_case}): {statement}",
            "Base case verification",
        )
        if not result:
            raise ValueError("Base case verification failed")
    
    def add_inductive_hypothesis(self, statement: str) -> None:
        """Add inductive hypothesis"""
        self.add_step(
            f"Assume P({self.inductive_var}): {statement}",
            "Inductive hypothesis"
        )
    
    def add_inductive_step(self, statement: str, verification: Callable[[int], bool],
                          test_values: List[int] = None) -> None:
        """Add and verify inductive step"""
        # Test inductive step for some values
        test_values = test_values or [self.base_case, self.base_case + 1, self.base_case + 2]
        for n in test_values:
            if not verification(n):
                raise ValueError(f"Inductive step verification failed for n={n}")
                
        self.add_step(
            f"Show P({self.inductive_var} + 1): {statement}",
            "Inductive step verification",
        )

class ContradictionProof(MathematicalProof):
    """Specialized class for proofs by contradiction"""
    
    def __init__(self):
        super().__init__(ProofType.CONTRADICTION)
    
    def add_contradiction(self, statement1: str, statement2: str,
                         step1: int, step2: int) -> None:
        """Add contradiction between two statements"""
        self.add_step(
            f"Contradiction: {statement1} contradicts {statement2}",
            "Logical contradiction",
            [step1, step2]
        )

def example_infinite_primes():
    """Prove there are infinitely many primes by contradiction"""
    proof = ContradictionProof()
    
    # Set up the proof
    proof.add_assumption("There are finitely many primes")
    proof.add_step(
        "Let p₁, p₂, ..., pₙ be all the primes",
        "From assumption"
    )
    proof.add_step(
        "Let N = (p₁ × p₂ × ... × pₙ) + 1",
        "Construction"
    )
    proof.add_step(
        "N is either prime or composite",
        "Fundamental theorem of arithmetic"
    )
    proof.add_step(
        "If N is prime, we found a prime not in our list",
        "Logical deduction",
        [1, 2]
    )
    proof.add_step(
        "If N is composite, it has a prime factor p",
        "Fundamental theorem of arithmetic"
    )
    proof.add_step(
        "p cannot be any of p₁, p₂, ..., pₙ (would leave remainder 1)",
        "Number theory",
        [2, 5]
    )
    proof.add_step(
        "We found a prime not in our list",
        "Logical deduction",
        [5, 6]
    )
    proof.add_contradiction(
        "There exists a prime not in our list",
        "List contains all primes",
        7, 1
    )
    
    proof.set_conclusion("There are infinitely many primes")
    return proof

def example_sum_squares_induction():
    """Prove sum of first n squares formula by induction"""
    proof = InductionProof()
    
    def verify_base(n: int) -> bool:
        return 1 == (n * (n + 1) * (2*n + 1)) // 6
    
    def verify_step(n: int) -> bool:
        sum_n = (n * (n + 1) * (2*n + 1)) // 6
        sum_n1 = ((n + 1) * (n + 2) * (2*n + 3)) // 6
        return sum_n + (n + 1)**2 == sum_n1
    
    # Set up the proof
    proof.add_base_case(
        "1² = 1 = (1 × 2 × 3)/6",
        verify_base
    )
    proof.add_inductive_hypothesis(
        "Σk² = n(n+1)(2n+1)/6 for k from 1 to n"
    )
    proof.add_inductive_step(
        "Σk² = (n+1)(n+2)(2n+3)/6 for k from 1 to n+1",
        verify_step
    )
    
    proof.set_conclusion(
        "For all n ≥ 1, sum of squares = n(n+1)(2n+1)/6"
    )
    return proof

if __name__ == "__main__":
    # Demonstrate infinite primes proof
    prime_proof = example_infinite_primes()
    prime_proof.display()
    
    print("\nProof verification:", prime_proof.verify())
    
    # Demonstrate sum of squares proof
    squares_proof = example_sum_squares_induction()
    squares_proof.display()

    
    print("\nProof verification:", squares_proof.verify())
```
