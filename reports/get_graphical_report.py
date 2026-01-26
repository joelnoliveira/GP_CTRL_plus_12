import pandas as pd
import matplotlib.pyplot as plt

def main():
	df = pd.read_csv('total_time_report.csv')

	# Convert minutes to hours
	df['Total Actual Time (hours)'] = df['Total Actual Time (min)'] / 60.0

	df['Name (Real names)'] = ["Diogo Pinto", "Francisco Coelho", "Diogo Frazão", "Giovanni Maffeo", "Joel Oliveira", "Raul Rodrigues", "Pedro Leixo", "João Santos", 
							"João Carvalho", "Tiago Conceição", "Tomás Azougado", "Tomé Ferreira"]

	plt.figure(figsize=(12, 6))

	# Generate distinct colors
	colors = plt.cm.tab20(range(len(df)))  # supports up to 20 distinct colors

	# Bar chart with different colors
	plt.bar(
		df['Name (Real names)'],
		df['Total Actual Time (hours)'],
		color=colors
	)

	# Horizontal line at y = 70 hours
	plt.axhline(y=70, linestyle='--', linewidth=2)

	plt.ylabel('Tempo gasto (horas)')
	plt.xlabel('Nome')
	plt.xticks(rotation=45, ha='right')
	plt.tight_layout()

	plt.show()

if __name__ == '__main__':
	main()
