import sys

class MainFunctionManager:
    """
    Manages multiple main functions with explicit execution control
    """
    
    @classmethod
    def register_main(cls, name):
        """
        Decorator to register main functions
        
        Usage:
        @MainFunctionManager.register_main('function_name')
        def some_main_function():
            ...
        """
        def decorator(func):
            # Ensure _mains dictionary exists
            if not hasattr(cls, '_mains'):
                cls._mains = {}
            
            # Register the function
            cls._mains[name] = func
            return func
        return decorator
    
    @classmethod
    def run_main(cls, name=None):
        """
        Run a specific main function or list available functions
        
        Parameters:
        name (str, optional): Name of main function to run
        """
        # Ensure _mains dictionary exists
        if not hasattr(cls, '_mains'):
            cls._mains = {}
        
        # If no name provided, list available functions
        if name is None:
            print("Available main functions:")
            for func_name in cls._mains.keys():
                print(f"- {func_name}")
            return
        
        # Run specific main function
        if name in cls._mains:
            cls._mains[name]()
        else:
            print(f"No main function named '{name}'")
    
    @classmethod
    def run_all_mains(cls):
        """
        Run all registered main functions
        """
        if not hasattr(cls, '_mains'):
            print("No main functions registered.")
            return
        
        for name, func in cls._mains.items():
            print(f"\n--- Running Main Function: {name} ---")
            func()

# Example usage with registration
@MainFunctionManager.register_main('data_processing')
def main_data_processing():
    """
    Main function for data processing
    """
    print("Processing data...")
    data = [1, 2, 3, 4, 5]
    processed_data = [x * 2 for x in data]
    print("Processed data:", processed_data)

@MainFunctionManager.register_main('network_analysis')
def main_network_analysis():
    """
    Main function for network analysis
    """
    print("Performing network analysis...")
    network = {
        'nodes': 10,
        'edges': 15
    }
    print("Network stats:", network)

@MainFunctionManager.register_main('visualization')
def main_visualization():
    """
    Main function for data visualization
    """
    print("Creating visualizations...")
    import matplotlib.pyplot as plt
    
    # Simple plot
    plt.figure(figsize=(8, 4))
    plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
    plt.title('Sample Visualization')
    plt.show()

def main():
    """
    Primary execution point with multiple options
    """
    # Parse command-line arguments
    if len(sys.argv) > 1:
        # Run specific main function
        MainFunctionManager.run_main(sys.argv[1])
    else:
        # Run all main functions
        MainFunctionManager.run_all_mains()

# Execution entry point
if __name__ == "__main__":
    main()

# Additional ways to run:
# 1. python script.py               (runs all mains)
# 2. python script.py data_processing  (runs specific main)
# 3. From another script:
#    from this_script import MainFunctionManager
#    MainFunctionManager.run_main('data_processing')
