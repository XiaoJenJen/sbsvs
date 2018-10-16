Security backtest and strategy visualization system

A trading simulator and visulization tool for security market
Technical stack: Python, Matplotlib.pyplot, Matplotlib.finance

(pic1)

h1: Project structure
	analysis.py: trading simulator
	config.py: paths for data
	data_processing.py: parse financial data and stock history into memory
	execute_data_processing: a bash script to batch pre-process the data
	visualization.py: plot trade records
	visualizations/: saved visualized trade records in pdf format
	results/: simulation results, including raw trade records and profit/time distribution.

h1: Trading simulator
	Strategy is written/hardcoded in analysis.py and self documented.

h1: Visulization
	Matplotlib 1.5 is used in this project. Please notice that Matplotlib is not backward compatible so newer version may not be supported. 
	Resulting plot sample is shown in visualizations/ folder and in each graph, the candlestick figure of a stock, buy/sell date and their price, profit is shown and the financial information at the buy date is listed in the up left corner. All contents are self-explained.

