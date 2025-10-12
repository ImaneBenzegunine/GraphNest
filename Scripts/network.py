import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

# Load your existing data
users = pd.read_csv('data/clean_data/users_clean.csv')
companies = pd.read_csv('data/clean_data/companies_clean.csv')
jobs = pd.read_csv('data/clean_data/jobs_clean.csv')
employment = pd.read_csv('data/clean_data/employment_clean.csv')

# Convert string representations of dictionaries to actual dictionaries
def parse_skills(skill_str):
    try:
        return eval(skill_str) if isinstance(skill_str, str) else {}
    except:
        return {}

users['skills'] = users['skills'].apply(parse_skills)
companies['required_skills'] = companies['required_skills'].apply(parse_skills)
jobs['required_skills'] = jobs['required_skills'].apply(parse_skills)
employment['skills_used'] = employment['skills_used'].apply(parse_skills)

# Create the professional network graph
G = nx.Graph()

# Add users as nodes with attributes
for _, user in users.iterrows():
    G.add_node(f"user_{user['user_id']}", 
              type='user',
              name=user['name'],
              job_title=user['job_title'],
              company=user['company'],
              skills=user['skills'])

# Add companies as nodes
for _, company in companies.iterrows():
    G.add_node(f"company_{company['company_id']}", 
              type='company',
              name=company['name'],
              required_skills=company['required_skills'])

# Add employment relationships as edges
for _, emp in employment.iterrows():
    G.add_edge(f"user_{emp['user_id']}", 
              f"company_{emp['company_id']}",
              type='employment',
              position=emp['position'],
              start_date=emp['start_date'],
              end_date=emp['end_date'])

# Calculate user-user connections based on shared skills and companies
def add_professional_connections(G):
    # Create skill index
    skill_to_users = defaultdict(list)
    for node in G.nodes():
        if G.nodes[node]['type'] == 'user':
            for skill in G.nodes[node]['skills']:
                skill_to_users[skill].append(node)
    
    # Connect users who share skills
    for skill, users in skill_to_users.items():
        if len(users) > 1:
            for i in range(len(users)):
                for j in range(i+1, len(users)):
                    u1, u2 = users[i], users[j]
                    if not G.has_edge(u1, u2):
                        skill_overlap = set(G.nodes[u1]['skills'].keys()) & set(G.nodes[u2]['skills'].keys())
                        G.add_edge(u1, u2,
                                  type='connection',
                                  reason='shared_skills',
                                  weight=len(skill_overlap))
    
    # Connect users at same company
    company_to_users = defaultdict(list)
    for node in G.nodes():
        if G.nodes[node]['type'] == 'user' and G.nodes[node]['company']:
            company_to_users[G.nodes[node]['company']].append(node)
    
    for company, users in company_to_users.items():
        if len(users) > 1:
            for i in range(len(users)):
                for j in range(i+1, len(users)):
                    u1, u2 = users[i], users[j]
                    if not G.has_edge(u1, u2):
                        G.add_edge(u1, u2,
                                  type='connection',
                                  reason='same_company',
                                  weight=3)  # Stronger weight for company connections

add_professional_connections(G)

# Analyze the graph
print("\nNetwork Analysis:")
print(f"Total nodes: {G.number_of_nodes()}")
print(f"Total edges: {G.number_of_edges()}")
print(f"User nodes: {len([n for n in G.nodes() if G.nodes[n]['type'] == 'user'])}")
print(f"Company nodes: {len([n for n in G.nodes() if G.nodes[n]['type'] == 'company'])}")

# Calculate centrality measures
degree_centrality = nx.degree_centrality(G)
betweenness_centrality = nx.betweenness_centrality(G, k=100)  # Sampling for performance
pagerank = nx.pagerank(G)

# Get top influential users
top_users = sorted(
    [(n, pagerank[n]) for n in G.nodes() if G.nodes[n]['type'] == 'user'],
    key=lambda x: x[1],
    reverse=True
)[:5]

print("\nTop 5 Influential Users:")
for user, score in top_users:
    print(f"{G.nodes[user]['name']} (Score: {score:.4f}) - {G.nodes[user]['job_title']} at {G.nodes[user]['company']}")

# Visualize a subgraph (for larger graphs, visualize a sample)
plt.figure(figsize=(12, 10))

# Get a sample of the graph for visualization
sample_nodes = (
    [n for n in G.nodes() if G.nodes[n]['type'] == 'user'][:20] +
    [n for n in G.nodes() if G.nodes[n]['type'] == 'company'][:5]
)
H = G.subgraph(sample_nodes)

# Color nodes by type
node_colors = []
for node in H.nodes():
    if H.nodes[node]['type'] == 'user':
        node_colors.append('lightblue')
    else:
        node_colors.append('lightgreen')

# Draw the graph
pos = nx.spring_layout(H, k=0.5, iterations=50)
nx.draw(H, pos, with_labels=True, node_color=node_colors, 
        node_size=800, font_size=10, edge_color='gray')
plt.title("Professional Network Sample")
plt.show()

# Save graph metrics to CSV
metrics = []
for node in G.nodes():
    if G.nodes[node]['type'] == 'user':
        metrics.append({
            'user_id': node.split('_')[1],
            'name': G.nodes[node]['name'],
            'degree_centrality': degree_centrality.get(node, 0),
            'betweenness_centrality': betweenness_centrality.get(node, 0),
            'pagerank': pagerank.get(node, 0),
            'company': G.nodes[node]['company']
        })

metrics_df = pd.DataFrame(metrics)
metrics_df.to_csv('data/processed/network_metrics.csv', index=False)
print("\nSaved network metrics to data/processed/network_metrics.csv")