# visualization_manager.py: Handles visualization data for teams

class VisualizationManager:
    """
    Manages the creation of visualization data for team histories.
    Extracts and formats data from team history for charts and visualizations.
    """
    
    @staticmethod
    def get_team_visualizations(team_data):
        """Get visualization data for a specific team.
        
        Args:
            team_data: Dict containing team state and history
            
        Returns:
            Dict containing formatted data for various visualizations
        """
        # Combine history and current state for full data series
        full_history = team_data["history"] + [team_data["current_state"]]

        # Extract data needed for charts based on specs.md
        years = [s['Year'] for s in full_history if 'Year' in s]
        gdp = [s['GDP'] for s in full_history if 'GDP' in s]
        nx = [s['Net Exports'] for s in full_history if 'Net Exports' in s]
        cons = [s['Consumption'] for s in full_history if 'Consumption' in s]
        savings = [s['Investment'] - s['Net Exports'] for s in full_history if 'Investment' in s and 'Net Exports' in s]  # Savings = Investment - NX = s*Y

        # Ensure all lists have the same length, potentially by padding or careful extraction
        # Simple approach: only include rounds where all data is present
        valid_indices = [i for i, s in enumerate(full_history) if all(k in s for k in ['Year', 'GDP', 'Net Exports', 'Consumption', 'Investment'])]

        if not valid_indices:
             return {"error": "Insufficient historical data for visualization"}

        years = [full_history[i]['Year'] for i in valid_indices]
        gdp = [full_history[i]['GDP'] for i in valid_indices]
        nx = [full_history[i]['Net Exports'] for i in valid_indices]
        cons = [full_history[i]['Consumption'] for i in valid_indices]
        savings = [(full_history[i]['Investment'] - full_history[i]['Net Exports']) for i in valid_indices]

        # Calculate GDP Growth (%) for visualization
        gdp_growth = [0.0]  # Growth for the first year is 0
        for i in range(1, len(gdp)):
            if gdp[i-1] != 0:
                growth = ((gdp[i] / gdp[i-1])**(1/5) - 1) * 100  # Annualized growth over 5 years
            else:
                growth = 0.0
            gdp_growth.append(growth)

        # Get latest consumption and savings for pie chart
        latest_cons = cons[-1] if cons else 0
        latest_savings = savings[-1] if savings else 0

        vis_data = {
            "gdp_growth_chart": {
                "years": years,
                "gdp_growth_percent": gdp_growth
            },
            "trade_balance_chart": {
                "years": years,
                "net_exports": nx
            },
            "consumption_savings_pie": {
                "consumption": latest_cons,
                "savings": latest_savings
            }
        }

        return vis_data 