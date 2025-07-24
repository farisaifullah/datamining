from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
from io import StringIO
from sklearn.tree import DecisionTreeClassifier
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
import uuid

app = Flask(__name__, static_folder='static')

DATAFRAME = None
VIS_DIR = "static/vis"
os.makedirs(VIS_DIR, exist_ok=True)

def save_plot(fig):
    vis_id = str(uuid.uuid4())
    path = os.path.join(VIS_DIR, f"{vis_id}.png")
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)
    return f"/vis/{vis_id}.png"

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/vis/<path:path>')
def serve_vis(path):
    return send_from_directory(VIS_DIR, path)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    s = file.read().decode('utf-8')
    global DATAFRAME
    DATAFRAME = pd.read_csv(StringIO(s))
    rows = DATAFRAME.head(10).replace([float('inf'), float('-inf')], None).fillna("").to_dict(orient="records")
    return jsonify({
        "columns": list(DATAFRAME.columns),
        "rows": rows
    })

@app.route('/mining', methods=['POST'])
def mining():
    global DATAFRAME
    if DATAFRAME is None:
        return jsonify({"error": "No data uploaded"})
    req = request.json
    method = req.get('method', '')
    params = req.get('params', {})
    df = DATAFRAME.copy()
    output = {}

    if method == 'decision_tree':
        X = df.select_dtypes(include='number').drop('Survived', axis=1, errors='ignore').fillna(0)
        y = df['Survived'] if 'Survived' in df.columns else None
        if y is None:
            output['error'] = "Kolom Survived tidak ditemukan."
        else:
            model = DecisionTreeClassifier(max_depth=3)
            model.fit(X, y)
            importances = dict(zip(X.columns, model.feature_importances_))
            output['result'] = "Model Decision Tree telah dilatih untuk memprediksi penumpang selamat."
            output['feature_importances'] = importances
            output['explanation'] = "Semakin besar angka pada feature importances, semakin penting kolom tersebut dalam memprediksi siapa yang selamat."
            # Visualisasi
            fig, ax = plt.subplots()
            imp = pd.Series(model.feature_importances_, index=X.columns)
            imp.sort_values().plot(kind='barh', ax=ax, color='#3575d3')
            ax.set_title("Feature Importances")
            ax.set_xlabel("Importance")
            fig.tight_layout()
            output['visual'] = save_plot(fig)
    elif method == 'kmeans':
        n_clusters = int(params.get('n_clusters', 2))
        X = df.select_dtypes(include='number').fillna(0)
        if X.shape[0] < n_clusters:
            output['error'] = "Jumlah data lebih sedikit dari jumlah cluster."
        else:
            kmeans = KMeans(n_clusters=n_clusters, n_init=10)
            labels = kmeans.fit_predict(X)
            output['result'] = f"Clustering selesai - Penumpang dikelompokkan menjadi {n_clusters} kelompok."
            output['labels'] = labels.tolist()[:20]
            output['explanation'] = "Setiap penumpang akan masuk ke salah satu cluster. Cluster adalah kelompok penumpang dengan data mirip."
            # Visualisasi
            fig, ax = plt.subplots()
            if X.shape[1] >= 2:
                sns.scatterplot(x=X.iloc[:, 0], y=X.iloc[:, 1], hue=labels, palette='tab10', ax=ax)
                ax.set_title("KMeans Clustering (2 fitur pertama)")
                ax.set_xlabel(X.columns[0])
                ax.set_ylabel(X.columns[1])
                fig.tight_layout()
                output['visual'] = save_plot(fig)
            else:
                output['visual'] = None
    elif method == 'linear_regression':
        if 'Fare' not in df.columns:
            output['error'] = "Kolom Fare tidak ditemukan."
        else:
            features = [col for col in df.select_dtypes(include='number').columns if col != 'Fare']
            X = df[features].fillna(0)
            y = df['Fare'].fillna(0)
            model = LinearRegression()
            model.fit(X, y)
            output['result'] = "Regresi linier mencari faktor apa yang mempengaruhi harga tiket."
            output['coeff'] = dict(zip(features, model.coef_))
            output['explanation'] = "Koefisien positif berarti faktor menaikkan harga tiket, negatif menurunkan. Bandingkan angka untuk tahu faktor paling berpengaruh."
            # Visualisasi
            y_pred = model.predict(X)
            fig, ax = plt.subplots()
            ax.scatter(y, y_pred, alpha=0.6, color='#3575d3')
            ax.set_xlabel("Harga Tiket Aktual")
            ax.set_ylabel("Harga Tiket Prediksi")
            ax.set_title("Prediksi Linear Regression vs Aktual")
            fig.tight_layout()
            output['visual'] = save_plot(fig)
    else:
        output['error'] = "Metode tidak dikenali."

    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)