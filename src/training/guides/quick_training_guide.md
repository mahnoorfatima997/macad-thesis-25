# 🚀 Quick Training Guide: 10-15 Images to Professional AI

## **What You Need Right Now**

### **1. Your Training Images (10-15 architectural drawings)**
```
training_images/
├── plan_001.jpg          # Floor plan
├── plan_002.jpg          # Floor plan  
├── elevation_001.jpg     # Building elevation
├── elevation_002.jpg     # Building elevation
├── section_001.jpg       # Building section
└── ... (10-15 total)
```

### **2. Annotations (YOLO format)**
For each image, create a `.txt` file with the same name:
```
plan_001.txt:
0 0.25 0.5 0.1 0.2    # door at (25%, 50%) with size (10%, 20%)
1 0.6 0.3 0.15 0.15   # window at (60%, 30%) with size (15%, 15%)
2 0.1 0.1 0.8 0.8     # wall at (10%, 10%) with size (80%, 80%)
```

### **3. Class Mapping**
```
0: door
1: window  
2: wall
3: stairs
4: toilet
5: kitchen
6: bedroom
7: living_room
8: corridor
9: entrance
10: exit
```

## **Step-by-Step Training Process**

### **Step 1: Prepare Your Dataset (30 minutes)**

1. **Create training directory structure:**
```bash
mkdir -p training_data/{images,labels}
mkdir -p training_data/images/{train,val}
mkdir -p training_data/labels/{train,val}
```

2. **Split your images:**
- Put 8-12 images in `training_data/images/train/`
- Put 2-3 images in `training_data/images/val/`

3. **Create corresponding labels:**
- Put annotation files in `training_data/labels/train/`
- Put annotation files in `training_data/labels/val/`

### **Step 2: Create Dataset Config (5 minutes)**

Create `training_data/dataset.yaml`:
```yaml
path: ./training_data
train: images/train
val: images/val

nc: 11  # number of classes
names: ['door', 'window', 'wall', 'stairs', 'toilet', 'kitchen', 'bedroom', 'living_room', 'corridor', 'entrance', 'exit']
```

### **Step 3: Train Your Model (2-4 hours)**

```python
from ultralytics import YOLO

# Load pre-trained model
model = YOLO('yolov8n.pt')

# Fine-tune on your architectural data
results = model.train(
    data='training_data/dataset.yaml',
    epochs=50,           # Start with 50 epochs
    imgsz=640,
    batch=4,             # Smaller batch for limited data
    name='architectural_yolo_quick',
    patience=20,         # Stop if no improvement
    save_period=10,      # Save every 10 epochs
    device='auto'
)
```

### **Step 4: Test Your Model (10 minutes)**

```python
# Test on a new image
results = model('test_plan.jpg')
results[0].show()  # Show detections
```

## **Annotation Tools You Can Use**

### **Option 1: LabelImg (Free, Easy)**
```bash
pip install labelImg
labelImg training_data/images/train/
```

### **Option 2: Roboflow (Online, Free tier)**
- Upload your images
- Draw bounding boxes
- Export in YOLO format

### **Option 3: CVAT (Advanced)**
- More features
- Better for larger datasets

## **Expected Results**

### **With 10-15 Images:**
- **Accuracy**: 60-75% (much better than generic 30-40%)
- **Detection**: Will recognize doors, windows, walls
- **Limitations**: May miss complex elements, needs more data

### **Next Steps After Quick Training:**
1. **Test on new images** - see what works/doesn't
2. **Add more images** - expand to 50-100 images
3. **Refine annotations** - improve quality
4. **Retrain** - better results

## **Integration with Your Current System**

### **Replace Generic YOLO:**
```python
# In your app.py or detection scripts
# Change from:
model = YOLO('yolov8n.pt')

# To:
model = YOLO('runs/detect/architectural_yolo_quick/weights/best.pt')
```

### **Update Class Names:**
```python
# Your system will now detect architectural elements instead of generic objects
architectural_classes = ['door', 'window', 'wall', 'stairs', 'toilet', 'kitchen', 'bedroom', 'living_room', 'corridor', 'entrance', 'exit']
```

## **Pro Tips for Small Datasets**

### **1. Data Augmentation (Automatic)**
YOLO automatically applies:
- Random rotation
- Color jittering
- Scaling
- Flipping

### **2. Transfer Learning (Already Done)**
- Starting from `yolov8n.pt` (pre-trained on COCO)
- Much faster than training from scratch
- Better results with limited data

### **3. Overfitting Prevention**
- Use validation set (2-3 images)
- Monitor validation loss
- Stop early if overfitting

## **Troubleshooting**

### **Common Issues:**
1. **"No labels found"** - Check annotation file format
2. **"CUDA out of memory"** - Reduce batch size to 2
3. **"Poor results"** - Add more diverse images
4. **"Training too slow"** - Use smaller model (yolov8n.pt)

### **Success Metrics:**
- **mAP@0.5 > 0.6** = Good for small dataset
- **Precision > 0.7** = Detecting correct elements
- **Recall > 0.6** = Finding most elements

## **Next Level: Scale Up**

### **Phase 2: 50-100 Images (1 week)**
- Add more diverse architectural drawings
- Include different scales and styles
- Improve annotation quality

### **Phase 3: 500+ Images (1 month)**
- Use ReCo dataset (you already have it!)
- Professional-grade accuracy
- Multiple architectural element types

### **Phase 4: Specialized Models**
- Separate models for plans vs elevations
- Custom critique models
- Compliance checking models

---

**Start with 10-15 images today, and you'll see immediate improvement in your architectural analysis!** 🏗️ 