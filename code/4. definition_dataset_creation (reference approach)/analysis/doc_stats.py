import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# Set larger font size for plots
matplotlib.rc('xtick', labelsize=20)
matplotlib.rc('ytick', labelsize=20)
matplotlib.rc('legend', fontsize=18)
# set LaTeX font
matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['font.family'] = 'STIXGeneral'

# Load the CSV file into a pandas DataFrame
df = pd.read_csv("definitions_per_document_final.csv", delimiter=";")

# Count the frequency of each attribute value
definition_counts = df['actual_count'].value_counts().sort_index()

# Calculate the mean and standard deviation for each attribute
mean_fragment_length = df['actual_count'].mean()
std_fragment_length = df['actual_count'].std()

# # Create a bar plot for Fragment Length
fig, ax = plt.subplots(figsize=(8, 6))
ax.bar(definition_counts.index, definition_counts.values, color="#1b9e77")
ax.axvline(mean_fragment_length, color='r', linestyle='solid', linewidth=2, label='Mean')
ax.axvline(mean_fragment_length + std_fragment_length, color='g', linestyle='dashed', linewidth=2, label='Std Dev')
ax.axvline(mean_fragment_length - std_fragment_length, color='g', linestyle='dashed', linewidth=2)
ax.set_xlabel('# of Definitions', fontsize = 16)
ax.set_ylabel('# of Documents', fontsize = 16)
ax.set_title('Distribution of definitions in Energy domain', fontsize = 18)
ax.legend(fontsize = 16)
ax.set_xlim(min(definition_counts.index)-1, max(definition_counts.index)+1)
plt.savefig("definition_distribution_new.png", dpi=400)
plt.show()

# Create a histogram for the attribute values
plt.figure(figsize=(8, 6))  # Adjust the figure size as needed
plt.hist(definition_counts.index, bins=20, color="#1b9e77")
plt.axvline(mean_fragment_length, color='r', linestyle='solid', linewidth=2, label='Mean')
plt.axvline(mean_fragment_length - std_fragment_length, color='g', linestyle='dotted', linewidth=1, label='Std Dev' )
plt.axvline(mean_fragment_length + std_fragment_length, color='g', linestyle='dotted', linewidth=1)
plt.xlabel('# of Definitions', fontsize = 16)
plt.ylabel('# of Documents', fontsize = 16)
plt.title('Distribution of definitions in Energy domain', fontsize = 18)
plt.legend(fontsize = 16)
plt.xlim(min(definition_counts.index)-1, max(definition_counts.index)+1)
plt.savefig("definition_histogram_distribution_new.png", dpi=400)
plt.show()