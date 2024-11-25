from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
import os

app = FastAPI()

class WineDataFilter:
    def __init__(self, csv_file: str):
        self.data = pd.read_csv(csv_file)
    
    def filter_by_quality(self, quality: int) -> pd.DataFrame:
        return self.data[self.data['quality'] == quality]
    
    def visualize_distribution(self, filtered_data: pd.DataFrame, features: List[str], output_file: str):
        fig, axes = plt.subplots(nrows=len(features), ncols=1, figsize=(8, 5 * len(features)))
        for i, feature in enumerate(features):
            axes[i].hist(filtered_data[feature], bins=30, color='skyblue', edgecolor='black')
            axes[i].set_title(f'Distribution of {feature}')
            axes[i].set_xlabel(feature)
            axes[i].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig(output_file)
        plt.close()

wine_filter = WineDataFilter(csv_file='winequality.csv')

class FilterRequest(BaseModel):
    quality: int
    features: List[str]


@app.get("/")
async def root():
    return {"message" : "Hello, Docker"}

@app.post("/filter-wine/")
async def filter_wine(filter_request: FilterRequest):
    try:
        filtered_data = wine_filter.filter_by_quality(filter_request.quality)
        if filtered_data.empty:
            raise HTTPException(status_code=404, detail="No data found for the given quality")
        
        output_file = f"quality_{filter_request.quality}_distribution.png"
        
        wine_filter.visualize_distribution(filtered_data, filter_request.features, output_file)
        
        if not os.path.exists(output_file):
            raise HTTPException(status_code=500, detail="Failed to save the visualization")
        
        return {
            "filtered_data": filtered_data.to_dict(orient="records"),
            "visualization": output_file
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


