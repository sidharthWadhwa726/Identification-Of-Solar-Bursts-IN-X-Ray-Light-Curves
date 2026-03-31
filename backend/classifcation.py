    # flare_clustering_pipeline.py
    import pandas as pd
    import numpy as np
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    import matplotlib.pyplot as plt
    import seaborn as sns
    import joblib
    import os 

    classified_test_data = pd.DataFrame() 
    # Step 1: Feature engineering function
    def compute_features(df):
        """
        Compute additional features: duration, starting, ending.
        """
        df = df.copy()
        df['starting'] = df['PeakTime'] - df['StartFWTM']
        df['ending'] = df['EndFWTM'] - df['PeakTime']
        df['duration'] = df['EndFWTM'] - df['StartFWTM']
        return df

    # Step 2: Training function

    def train_clustering(df_train, n_clusters=4):
        df_train = compute_features(df_train)
        features = ['PeakFlux', 'FittedSNR', 'DecayTau', 'RiseSigma', 'R_squared', 'duration', 'starting']
        X_train = df_train[features]
        # scaling the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_train)

        # Train KMeans
        # Suppress the FutureWarning about explicit n_init being required
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
        df_train['Cluster'] = kmeans.fit_predict(X_scaled)
        df_train['Predicted_Cluster'] = df_train['Cluster']

        # Save artifacts
        joblib.dump(scaler, 'scaler.pkl')
        joblib.dump(kmeans, 'kmeans_model.pkl')

        # Visualize clusters
        plt.figure(figsize=(10,6))
        sns.scatterplot(data=df_train, x='DecayTau', y='PeakFlux', hue='Cluster', palette='Set2', s=100)
        plt.title('Clusters of Flares (Training Data)')
        plt.show()

        # Optional: print cluster centers in original scale
        centers = scaler.inverse_transform(kmeans.cluster_centers_)
        cluster_centers = pd.DataFrame(centers, columns=features)
        print("Cluster Centers (original scale):")
        print(cluster_centers)

        # Save clustered training data
        df_train.to_csv('training_data_clustered.csv', index=False)
        print("[OK] Training complete and artifacts saved.")
        
        # Returning a generic map (Placeholder)
        return {i: f'Cluster {i}' for i in range(n_clusters)}

    # Step 3: Testing function (with Solar Class Mapping)

    def test_clustering(df_test, cluster_to_solar_class):
        if not os.path.exists('scaler.pkl') or not os.path.exists('kmeans_model.pkl'):
            if __name__ == "__main__":
                raise FileNotFoundError("Clustering artifacts (scaler.pkl or kmeans_model.pkl) not found. Run training first!")
            else:
                return pd.DataFrame() 
                
        scaler = joblib.load('scaler.pkl')
        kmeans = joblib.load('kmeans_model.pkl') 

        # Compute feature
        df_test = compute_features(df_test)
        features = ['PeakFlux', 'FittedSNR', 'DecayTau', 'RiseSigma', 'R_squared', 'duration', 'starting']
        X_test = df_test[features]

        # Scale and predict
        X_test_scaled = scaler.transform(X_test)
        df_test['Cluster'] = kmeans.predict(X_test_scaled)
        df_test['Predicted_Cluster'] = df_test['Cluster']

        # APPLY THE MAPPING TO THE CLUSTER COLUMN
        df_test['Solar_Class'] = df_test['Cluster'].map(cluster_to_solar_class)
        
        # VISUALIZE WITH NEW LABELS
        plt.figure(figsize=(10,6))
        sns.scatterplot(data=df_test, x='DecayTau', y='PeakFlux', hue='Solar_Class', palette='viridis', s=100)
        plt.title('Solar Class Predictions on Test Data')
        plt.show()

        # Save clustered test data, now with the 'Solar_Class' column
        df_test.to_csv('testing_data_classified.csv', index=False)
        print("[OK] Testing complete. Results saved with Solar Class labels to 'testing_data_classified.csv'.")
        
        return df_test # Return the classified DataFrame

    # Step 4: Main Execution
    if __name__ == "__main__":
        # Define the mapping dictionary based on the physical criteria
        SOLAR_CLASS_MAP = {
            0: 'A/B',
            1: 'C',   
            2: 'M',  
            3: 'X'    
        }

        # --- TRAINING ---
        try:
            df_train = pd.read_csv(r'C:\Users\sidharth\OneDrive\Desktop\internal_hackathon_ISRO\classification_dataset.csv')
            train_clustering(df_train, n_clusters=4)
            print("[Training Completed. Check cluster centers to confirm SOLAR_CLASS_MAP]")
        except Exception as e:
            print(f"Training failed: {e}")
            
        # --- TESTING ---
        try:
            df_test_raw = pd.read_csv('testing_data.csv')
            df_test = df_test_raw.rename(columns={'PeakFlux_nW/m2': 'PeakFlux'})
        
            global classified_test_data
            classified_test_data = test_clustering(df_test, SOLAR_CLASS_MAP)
            
            print("\n--- Final Classified Test Data (Sample) ---")
            display_cols = ['PeakFlux', 'DecayTau', 'duration', 'starting', 'Predicted_Cluster', 'Solar_Class']
            
            final_df_sample = classified_test_data.head(10)
            valid_display_cols = [col for col in display_cols if col in final_df_sample.columns]

            print(final_df_sample[valid_display_cols].round(2).to_markdown(index=False, numalign="left", stralign="left"))
            
            print("\nSolar Class Distribution:")
            print(classified_test_data['Solar_Class'].value_counts().to_markdown())
            
        except Exception as e:
            print(f"Testing failed: {e}")

    # This print statement will show the final DataFrame with the classes.
    print("\n--- Full Classified Test Data (Final Global Output) ---")
    # Check if the global DataFrame was populated before printing
    if not classified_test_data.empty:
        print(classified_test_data.round(2))
    else:
        print("DataFrame is empty, likely due to errors during the testing phase.")
    classified_test_data.to_csv('testing_data_classified.csv', index=False)
