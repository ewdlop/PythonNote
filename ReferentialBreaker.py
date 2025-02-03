import sys
from typing import List, Tuple, Optional
from dataclasses import dataclass
import random

@dataclass
class PolyVariant:
    name: str
    transform: callable
    expected_breaks: List[int]

class ReferentialBreaker:
    def __init__(self):
        self.variants = []
        self._setup_variants()
        
    def _setup_variants(self):
        # Base case - supposedly "pure"
        self.variants.append(
            PolyVariant(
                "pure_increment",
                lambda x: x + 1,
                []
            )
        )
        
        # Integer overflow variant
        self.variants.append(
            PolyVariant(
                "overflow_wrap",
                lambda x: (x + 1) & 0xFFFFFFFF,
                [0xFFFFFFFF, 0x7FFFFFFF]
            )
        )
        
        # Memory corruption variant
        def memory_corrupt(x):
            if x > 0xFFFFF000:
                # Simulate memory corruption
                return x ^ random.randint(0, 0xFFFF)
            return x + 1
            
        self.variants.append(
            PolyVariant(
                "memory_corrupt",
                memory_corrupt,
                [0xFFFFF001, 0xFFFFFFF0]
            )
        )
        
        # Register exhaustion variant
        def register_exhaust(x):
            # Simulate register pressure
            regs = [x]
            for i in range(8):  # Typical register count
                regs.append(regs[-1] + 1)
            if len(regs) > 7:
                # Register spill happens
                return regs[0] + 2  # Off by one error
            return x + 1
            
        self.variants.append(
            PolyVariant(
                "register_exhaust",
                register_exhaust,
                list(range(0xFF0, 0xFFF))
            )
        )
        
        # Cache timing variant
        def cache_timing(x):
            # Simulate cache effects
            if x % 64 == 0:  # Cache line size
                # Cache miss simulation
                return x + 2  # Wrong result due to race
            return x + 1
            
        self.variants.append(
            PolyVariant(
                "cache_timing",
                cache_timing,
                [x for x in range(0, 0x1000, 64)]
            )
        )

    def break_referential(self, test_range: Tuple[int, int]):
        start, end = test_range
        breaks = []
        
        print(f"Testing range 0x{start:X} to 0x{end:X}")
        
        for x in range(start, end):
            results = []
            for variant in self.variants:
                try:
                    result = variant.transform(x)
                    results.append(result)
                except Exception as e:
                    results.append(f"Error: {str(e)}")
                    
            # Check if all results match
            if len(set(str(r) for r in results)) > 1:
                breaks.append({
                    'input': hex(x),
                    'results': dict(zip([v.name for v in self.variants], results))
                })
                
        return breaks

def main():
    breaker = ReferentialBreaker()
    
    # Test ranges that are likely to break
    test_ranges = [
        (0x7FFFFFF0, 0x80000000),  # Around signed int max
        (0xFFFFFFF0, 0xFFFFFFFF),  # Around unsigned int max
        (0xFF000000, 0xFF000100),  # Memory boundary region
        (0x0, 0x1000),            # Cache line boundaries
    ]
    
    all_breaks = []
    for test_range in test_ranges:
        breaks = breaker.break_referential(test_range)
        all_breaks.extend(breaks)
        
    print("\nFound breaks in referential transparency:")
    for brk in all_breaks[:10]:  # Show first 10 breaks
        print(f"\nInput: {brk['input']}")
        for variant, result in brk['results'].items():
            print(f"  {variant}: {result}")

if __name__ == "__main__":
    main()
