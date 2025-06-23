#Ellipse fitting module
#Requires pandas, EllipseModel
import pandas as pd
import numpy as np
from skimage.measure import EllipseModel

def ellipse_fitting(mouse_file):
    # Ensure numeric values in the DataFrame
    mouse = mouse_file.iloc[:, :-12].copy()
    mouse = mouse.apply(pd.to_numeric, errors='coerce')
    
    # Convert to NumPy array for faster processing
    mouse = mouse.to_numpy()
    row_mouse = mouse.shape[0]
    
    # Create filtering matrix
    likelihood_columns = np.arange(3, mouse.shape[1], 3)  # Get index of likelihood columns
    likelihood_values = mouse[:, likelihood_columns]
    
    # Ensure all likelihood values are numeric (previously coerced to NaN if non-numeric)
    likelihood_values = np.nan_to_num(likelihood_values, nan=0.0)
    
    filtering_matrix = (np.roll(likelihood_values, -2, axis=0) >= 0.9).astype(int)[:-2]
    
    # Sum of filtering matrix across columns for each row
    filtering_matrix_sum = filtering_matrix.sum(axis=1)
    filtering_matrix_cond = filtering_matrix == 1

    model = EllipseModel()
    ellipse_results = []

    # Iterate through rows, but only process rows that meet filtering condition
    for f in range(row_mouse - 2):
        if filtering_matrix_sum[f] >= 6:
            # Collect points that meet the condition
            selection_points = []

            for i in range(12):
                if filtering_matrix_cond[f, i]:
                    countx = 1 + 3 * i
                    county = 2 + 3 * i
                    selection_points.append([mouse[f + 2, countx], mouse[f + 2, county]])

            # Fit ellipse if we have enough points
            if len(selection_points) >= 5:  # Minimum 5 points are needed to fit an ellipse
                selection_temp = np.array(selection_points, dtype=float)
                model.estimate(selection_temp)
                ellipse_params = list(model.params) + [f]
            else:
                ellipse_params = [np.nan, np.nan, np.nan, np.nan, np.nan, f]
        else:
            ellipse_params = [np.nan, np.nan, np.nan, np.nan, np.nan, f]

        ellipse_results.append(ellipse_params)

    # Convert results to DataFrame
    ellipse = pd.DataFrame(ellipse_results, columns=['X_Position', 'Y_Position', 'Radius_1', 'Radius_2', 'Angle', 'Time_Frames'])
    
    # Calculate 'Largest_Radius' using efficient vectorized operations
    mask_nan = ellipse['Radius_1'].isna()
    mask_else = ellipse['Radius_1'] > ellipse['Radius_2']
    ellipse['Largest_Radius'] = np.nan
    ellipse.loc[~mask_nan & ~mask_else, 'Largest_Radius'] = ellipse.loc[~mask_nan & ~mask_else, 'Radius_2']
    ellipse.loc[mask_else, 'Largest_Radius'] = ellipse.loc[mask_else, 'Radius_1']

    # Reorder columns
    ellipse_formatted = ellipse.copy()
    ellipse_formatted.insert(0, 'Time_Frames', ellipse_formatted.pop('Time_Frames'))

    return ellipse_formatted

