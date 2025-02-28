import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import os
from PIL import Image
import base64
import io
import json
import math



# Initialize the Dash app with callback exception suppression
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                assets_folder='assets',
                suppress_callback_exceptions=True)

def load_title_from_file(file_path="title.txt"):
    """Load the timeline title from a text file."""
    try:
        with open(file_path, 'r') as file:
            # Read the first line as the title
            title = file.read()
            return title if title else "Title"  # Default if empty
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. Using default title.")
        return "Title"
    except Exception as e:
        print(f"Error reading title from {file_path}: {e}")
        return "Title"
        
def load_desc_from_file(file_path="description.txt"):
    """Load the timeline title from a text file."""
    try:
        with open(file_path, 'r') as file:
            # Read the first line as the title
            title = file.read()
            return title if title else "description"  # Default if empty
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. Using default title.")
        return "description"
    except Exception as e:
        print(f"Error reading title from {file_path}: {e}")
        return "description"


# Load and preprocess functions remain the same
def load_data(csv_path):
    df = pd.read_csv(csv_path)
    df['PARSED_DATE'] = df['DATE'].apply(parse_date)
    df = df.sort_values('PARSED_DATE')
    return df

def parse_date(date_str):
    date_str = date_str.strip()
    if len(date_str) == 4:  # YYYY
        return datetime(int(date_str), 1, 1)
    elif len(date_str) == 7:  # YYYY-MM
        year, month = date_str.split('-')
        return datetime(int(year), int(month), 1)
    else:  # YYYY-MM-DD
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            parts = date_str.split('-')
            if len(parts) == 2:
                year, month = parts
                return datetime(int(year.strip()), int(month.strip()), 1)
            else:
                print(f"Could not parse date: '{date_str}'")
                return datetime(1900, 1, 1)

# Function to get images for an event
def get_event_images(event_id):
    images = []
    folder_path = f"./images/{event_id}"
    
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                img_path = os.path.join(folder_path, filename)
                try:
                    img = Image.open(img_path)
                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    images.append(f"data:image/jpeg;base64,{img_str}")
                except Exception as e:
                    print(f"Error loading image {img_path}: {e}")
    
    return images

# Load data
df = load_data("timeline.csv")

# Load title from text file
timeline_title = load_title_from_file()
timeline_desc = load_desc_from_file()

# Create assets folder if it doesn't exist
import os
os.makedirs('assets', exist_ok=True)

with open('assets/zigzag_timeline.css', 'w') as f:
    f.write('''
.zigzag-timeline {
    width: 100%;
    position: relative;
    padding: 20px;
}

.zigzag-row {
    display: flex;
    position: relative;
    margin-bottom: 50px; /* Fixed spacing between rows */
    padding-bottom: 0;
}

/* Horizontal line through each row */
.zigzag-row::before {
    content: '';
    position: absolute;
    height: 4px;
    background: #0d6efd;
    top: 50%;
    width: 95%;
    z-index: 1;
}

/* Odd rows (1st, 3rd, etc) - left to right */
.zigzag-row.odd::before {
    left: 0;
}

/* Even rows (2nd, 4th, etc) - right to left */
.zigzag-row.even::before {
    right: 0;
}

/* Vertical connector between rows - with negative margins to bridge the gap */
.row-connector {
    height: 70px; /* Base height */
    width: 4px;
    background-color: #0d6efd;
    margin-top: -25px; /* Pull up to overlap with row above */
    margin-bottom: -25px; /* Extend down to overlap with row below */
    z-index: 0;
    position: relative; /* Needed for z-index to work */
}

/* For odd rows (left-to-right), connect from right side */
.connector-odd-to-even {
    margin-left: auto;
    margin-right: 15px;
}

/* For even rows (right-to-left), connect from left side */
.connector-even-to-odd {
    margin-left: 15px;
    margin-right: auto;
}

.zigzag-item {
    flex: 1;
    margin: 0 15px;
    position: relative;
    z-index: 2;
}

.zigzag-item-content {
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    padding: 15px;
    position: relative;
    cursor: pointer;
    transition: all 0.3s ease;
    min-height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.zigzag-item-content:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
}

/* Remove all timeline circles */
.zigzag-item::after {
    display: none;
}

.zigzag-date {
    font-size: 0.85rem;
    color: #6c757d;
    margin-bottom: 5px;
}

.zigzag-title {
    font-weight: bold;
    margin-bottom: 10px;
    font-size: 1.1rem;
}

.zigzag-desc {
    font-size: 0.9rem;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
}

/* Image navigation buttons */
.image-nav-btn {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background: rgba(0,0,0,0.5);
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0.7;
    transition: opacity 0.3s;
}

.image-nav-btn:hover {
    opacity: 1;
}

.prev-btn {
    left: 10px;
}

.next-btn {
    right: 10px;
}

/* Image container */
.image-container {
    position: relative;
    min-height: 300px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 20px 0;
}

.image-counter {
    position: absolute;
    bottom: 10px;
    right: 10px;
    background: rgba(0,0,0,0.5);
    color: white;
    padding: 5px 10px;
    border-radius: 12px;
    font-size: 0.8rem;
}

/* Media query for mobile */
@media (max-width: 768px) {
    .zigzag-row {
        flex-direction: column;
    }
    
    .zigzag-row::before {
        width: 4px;
        height: 90%;
        top: 5%;
        left: 20px !important;
        right: auto !important;
    }
    
    .zigzag-item {
        margin: 20px 0 20px 50px;
    }
    
    .row-connector {
        display: none; /* Hide custom connectors on mobile */
    }
}
''')


app.layout = html.Div([
    dbc.Container([
        html.H1(timeline_title, className="my-4", style={"white-space": "pre-wrap"}),
        html.P(timeline_desc, className="my-5", style={"white-space": "pre-wrap"}),
        # Controls
        dbc.Row([
            dbc.Col([
                dbc.Label("Items per row:"),
                dcc.Slider(
                    id='items-per-row-slider',
                    min=2,
                    max=6,
                    step=1,
                    value=6,
                    marks={i: str(i) for i in range(2, 7)},
                ),
            ], width=6),
            dbc.Col([
                dbc.Label("Display density:"),
                dcc.Slider(
                    id='density-slider',
                    min=1,
                    max=5,
                    step=1,
                    value=5,
                    marks={1: 'Few', 3: 'Medium', 5: 'All'},
                ),
            ], width=6),
        ], className="mb-4"),
        
        # Search
        dbc.Row([
            dbc.Col([
                dbc.Input(id="search-input", placeholder="Search events...", type="text"),
            ], width=12),
        ], className="mb-4"),
        
        # Zigzag timeline container
        html.Div([
            html.Div(id='zigzag-timeline-container', className='zigzag-timeline')
        ], style={'overflow-y': 'auto', 'height': '70vh', 'padding': '20px 0'}),
        
        # Modal for event details with image navigation
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id="modal-title")),
            dbc.ModalBody([
                html.P(id="modal-date", className="text-muted"),
                html.P(id="modal-description"),
                html.Div([
                    # Image display div
                    html.Div(id="modal-image-display", className="text-center"),
                    # Image counter text
                    html.Div(id="image-counter", className="text-center mt-2"),
                    # Always include the navigation buttons but hide them as needed
                    html.Button("◀", id="prev-image-btn", 
                                className="image-nav-btn prev-btn", 
                                style={'display': 'none'}),
                    html.Button("▶", id="next-image-btn", 
                                className="image-nav-btn next-btn", 
                                style={'display': 'none'})
                ], id="modal-images-container", className="position-relative")
            ]),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0)
            ),
        ], id="event-modal", is_open=False, size="lg"),
        
        # Store for selected event - initialize with None to prevent autoload
        dcc.Store(id='selected-event-id', data=None),
        
        # Store for image navigation
        dcc.Store(id='event-images', data={"images": [], "current_index": 0}),
        
        # Flag to track if app has been loaded
        dcc.Store(id='app-loaded', data=False),
        
    ], fluid=True)
])

@app.callback(
    Output('zigzag-timeline-container', 'children'),
    [Input('items-per-row-slider', 'value'),
     Input('density-slider', 'value'),
     Input('search-input', 'value')]
)
def update_zigzag_timeline(items_per_row, density, search_term):
    # Filter by search term if provided
    filtered_df = df
    if search_term:
        search_term = search_term.lower()
        filtered_df = df[
            df['NAME'].str.lower().str.contains(search_term) | 
            df['EVENT'].str.lower().str.contains(search_term)
        ]
    
    # Sample events based on density
    if density == 5:  # Show all events
        visible_df = filtered_df
    else:
        # Adjust sample rate based on density
        step = 6 - density  # Higher density = more events
        indices = list(range(0, len(filtered_df), step))
        # Always include first and last for context
        if len(filtered_df) - 1 not in indices and len(filtered_df) > 0:
            indices.append(len(filtered_df) - 1)
        if 0 not in indices and len(filtered_df) > 0:
            indices.insert(0, 0)
        visible_df = filtered_df.iloc[indices].copy()
    
    # No events to display
    if len(visible_df) == 0:
        return html.Div("No events match your search criteria.", className="text-center py-5")
    
    # Create timeline rows
    timeline_rows = []
    num_rows = math.ceil(len(visible_df) / items_per_row)
    
    for row_idx in range(num_rows):
        row_class = "odd" if row_idx % 2 == 0 else "even"
        
        # Get items for this row
        start_idx = row_idx * items_per_row
        end_idx = min(start_idx + items_per_row, len(visible_df))
        row_items = visible_df.iloc[start_idx:end_idx]
        
        # Create timeline items for this row
        timeline_items = []
        display_items = row_items.iloc[::-1] if row_class == "even" else row_items
        
        for _, row in display_items.iterrows():
            timeline_items.append(
                html.Div([
                    html.Div([
                        html.Div(row['DATE'], className="zigzag-date"),
                        html.Div(row['NAME'], className="zigzag-title"),
                        html.Div(
                            row['EVENT'][:100] + "..." if len(row['EVENT']) > 100 else row['EVENT'], 
                            className="zigzag-desc"
                        )
                    ],
                    className="zigzag-item-content",
                    id={'type': 'timeline-event', 'index': row['ID']})
                ], className="zigzag-item")
            )
        
        # Create row
        row_div = html.Div(timeline_items, className=f"zigzag-row {row_class}")
        timeline_rows.append(row_div)
    
    # Add connector elements between rows
    final_elements = []
    
    for i, row in enumerate(timeline_rows):
        final_elements.append(row)
        
        # Add connector between rows (except after the last row)
        if i < len(timeline_rows) - 1:
            row_class = "odd" if i % 2 == 0 else "even"
            connector_class = "connector-odd-to-even" if row_class == "odd" else "connector-even-to-odd"
            
            # Calculate a taller connector based on row spacing
            connector_height = 100  # Base height
            
            final_elements.append(
                html.Div(className=f"row-connector {connector_class}",
                        style={"height": f"{connector_height}px"})
            )
    
    return final_elements



# Track if app has been loaded to prevent auto-popup
@app.callback(
    Output('app-loaded', 'data'),
    [Input('zigzag-timeline-container', 'children')]
)
def set_app_loaded(children):
    return True

# Callback to capture click on timeline item (fixed to prevent auto-triggering)
@app.callback(
    Output('selected-event-id', 'data'),
    [Input({'type': 'timeline-event', 'index': dash.dependencies.ALL}, 'n_clicks')],
    [State('selected-event-id', 'data'),
     State('app-loaded', 'data')],
    prevent_initial_call=True
)
def handle_timeline_click(n_clicks_list, current_event_id, app_loaded):
    ctx = callback_context
    
    # If not triggered by a click or app not fully loaded, don't do anything
    if not ctx.triggered or not app_loaded:
        return current_event_id
    
    # Check that any clicks actually happened
    if not any(click for click in n_clicks_list if click is not None):
        return current_event_id
    
    # Get the ID that was clicked
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    event_id = json.loads(trigger_id)['index']
    return event_id

# Updated modal toggle callback to prevent auto-opening
@app.callback(
    [Output("event-modal", "is_open"),
     Output("modal-title", "children"),
     Output("modal-date", "children"),
     Output("modal-description", "children"),
     Output("event-images", "data")],
    [Input("selected-event-id", "data"),
     Input("close-modal", "n_clicks")],
    [State("event-modal", "is_open"),
     State('app-loaded', 'data')]
)
def toggle_modal(event_id, close_clicks, is_open, app_loaded):
    ctx = callback_context
    
    # If app is not loaded yet, don't open anything
    if not app_loaded:
        return False, "", "", "", {"images": [], "current_index": 0}
    
    # Identify which input triggered the callback
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Handle close button click
    if trigger_id == "close-modal" and close_clicks:
        return False, "", "", "", {"images": [], "current_index": 0}
    
    # Handle click on a timeline event
    if trigger_id == "selected-event-id" and event_id is not None:
        # Find the row with this ID
        event_row = df[df['ID'] == int(event_id)]
        
        if not event_row.empty:
            name = event_row.iloc[0]['NAME']
            date = event_row.iloc[0]['DATE']
            description = event_row.iloc[0]['EVENT']
            
            # Get images for this event
            images = get_event_images(int(event_id))
            
            return True, name, f"Date: {date}", description, {"images": images, "current_index": 0}
    
    # Default case - maintain current state
    return is_open, "", "", "", {"images": [], "current_index": 0}

# Image display callback stays mostly the same
@app.callback(
    [Output("modal-image-display", "children"),
     Output("image-counter", "children"),
     Output("prev-image-btn", "style"),
     Output("next-image-btn", "style")],
    [Input("event-images", "data")]
)
def update_image_display(image_data):
    images = image_data.get("images", [])
    current_index = image_data.get("current_index", 0)
    
    # Default button style - hidden
    button_style = {'display': 'none'}
    
    # Image display content
    if not images:
        image_display = html.Div("No images available for this event.", 
                                className="text-center py-4")
        counter = ""
    else:
        # Show current image
        image_display = html.Div([
            html.Img(
                src=images[current_index],
                style={
                    'max-width': '100%',
                    'max-height': '400px',
                    'margin': '10px auto'
                }
            )
        ], className="image-container")
        
        # Image counter text
        counter = f"Image {current_index + 1} of {len(images)}" if len(images) > 1 else ""
        
        # Only show navigation buttons if there are multiple images
        if len(images) > 1:
            button_style = {
                'display': 'flex',
                'position': 'absolute',
                'top': '50%',
                'transform': 'translateY(-50%)',
                'background': 'rgba(0,0,0,0.5)',
                'color': 'white',
                'border': 'none',
                'borderRadius': '50%',
                'width': '40px',
                'height': '40px',
                'alignItems': 'center',
                'justifyContent': 'center',
                'opacity': '0.7',
                'zIndex': '10'
            }
    
    # Return all the outputs
    return image_display, counter, button_style, button_style

# Navigation callback stays the same
@app.callback(
    Output("event-images", "data", allow_duplicate=True),
    [Input("prev-image-btn", "n_clicks"),
     Input("next-image-btn", "n_clicks")],
    [State("event-images", "data")],
    prevent_initial_call=True
)
def navigate_images(prev_clicks, next_clicks, current_data):
    ctx = callback_context
    if not ctx.triggered:
        return current_data
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    images = current_data.get("images", [])
    current_index = current_data.get("current_index", 0)
    
    if not images or len(images) <= 1:
        return current_data
    
    if button_id == "prev-image-btn" and prev_clicks:
        # Go to previous image or wrap around to the last image
        new_index = (current_index - 1) % len(images)
    elif button_id == "next-image-btn" and next_clicks:
        # Go to next image or wrap around to the first image
        new_index = (current_index + 1) % len(images)
    else:
        new_index = current_index
    
    return {"images": images, "current_index": new_index}

if __name__ == '__main__':
    app.run_server(debug=True)
