# Complete Personality AI Implementation Package

## Project Overview

This document provides complete instructions for implementing a scientifically robust personality assessment AI system using HEXACO/Big Five models with visual artwork correlation. The system will analyze text input and provide personality trait predictions with corresponding visual representations.

## Table of Contents

1. [Scientific Framework](#scientific-framework)
2. [Implementation Resources](#implementation-resources)
3. [Technical Architecture](#technical-architecture)
4. [Artwork Correlation System](#artwork-correlation-system)
5. [Image Generation Specifications](#image-generation-specifications)
6. [Complete Source Citations](#complete-source-citations)
7. [Development Instructions](#development-instructions)

---

## Scientific Framework

### Primary Model: HEXACO (Recommended)

**Six Dimensions with Superior Cross-Cultural Validation:**

1. **Honesty-Humility (H)** - α = 0.88
   - Sincerity, fairness, greed-avoidance, modesty
2. **Emotionality (E)** - α = 0.85  
   - Fearfulness, anxiety, dependence, sentimentality
3. **eXtraversion (X)** - α = 0.87
   - Social self-esteem, social boldness, sociability, liveliness
4. **Agreeableness (A)** - α = 0.83
   - Forgiveness, gentleness, flexibility, patience
5. **Conscientiousness (C)** - α = 0.86
   - Organization, diligence, perfectionism, prudence
6. **Openness (O)** - α = 0.84
   - Aesthetic appreciation, inquisitiveness, creativity, unconventionality

### Secondary Model: Big Five (OCEAN)

**Five Dimensions - Widely Research-Supported:**

1. **Openness** - α = 0.83
2. **Conscientiousness** - α = 0.86
3. **Extraversion** - α = 0.85
4. **Agreeableness** - α = 0.80
5. **Neuroticism** - α = 0.89

---

## Implementation Resources

### Pre-trained Models (Ready to Use)

#### Option 1: Hugging Face - bert-base-personality
```python
from transformers import BertTokenizer, BertForSequenceClassification
import torch

# Model with 6,675+ monthly downloads
tokenizer = BertTokenizer.from_pretrained("Minej/bert-base-personality")
model = BertForSequenceClassification.from_pretrained("Minej/bert-base-personality")

def analyze_personality(text):
    inputs = tokenizer(text, truncation=True, padding=True, return_tensors="pt", max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    predictions = torch.sigmoid(outputs.logits).squeeze().numpy()
    
    traits = ['Extraversion', 'Neuroticism', 'Agreeableness', 'Conscientiousness', 'Openness']
    scores = {trait: float(score) for trait, score in zip(traits, predictions)}
    return scores
```

**Model URL:** https://huggingface.co/Minej/bert-base-personality

#### Option 2: Microsoft Fine-tuned (97% Accuracy Claimed)
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("Nasserelsaman/microsoft-finetuned-personality")
model = AutoModelForSequenceClassification.from_pretrained("Nasserelsaman/microsoft-finetuned-personality")
```

**Model URL:** https://huggingface.co/Nasserelsaman/microsoft-finetuned-personality

#### Option 3: Complete Pipeline - SenticNet Implementation
```bash
git clone https://github.com/SenticNet/personality-detection.git
cd personality-detection
pip install theano pandas numpy scikit-learn
python process_data.py ./GoogleNews-vectors-negative300.bin ./essays.csv
python conv_layer_train.py -static -word2vec
```

**Repository URL:** https://github.com/SenticNet/personality-detection

### Commercial APIs for Academic Use

#### Receptiviti API (Comprehensive)
- **URL:** https://www.receptiviti.com/api
- **Documentation:** https://docs.receptiviti.com/
- **Features:** 200+ psychological insights, Big Five + LIWC
- **Cost:** Academic pricing available

#### Apply Magic Sauce (Free for Academic)
- **URL:** https://applymagicsauce.com/about-us
- **Academic Access:** Free with university registration
- **Features:** Big Five from Cambridge research (6M+ profiles)

#### Crystal Knows API
- **URL:** https://www.crystalknows.com/app/developers
- **Features:** DISC, Enneagram, MBTI
- **Cost:** $499/month after 30 free calls

---

## Technical Architecture

### Project Structure
```
personality-ai-project/
├── README.md
├── requirements.txt
├── Dockerfile
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── personality_analyzer.py
│   │   ├── bert_classifier.py
│   │   └── ensemble_model.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── preprocessing.py
│   │   └── validation.py
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── artwork_correlator.py
│   │   └── plot_generator.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── endpoints.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       └── logging_config.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── artwork/
│       ├── hexaco/
│       │   ├── honesty_humility/
│       │   ├── emotionality/
│       │   ├── extraversion/
│       │   ├── agreeableness/
│       │   ├── conscientiousness/
│       │   └── openness/
│       └── big_five/
│           ├── openness/
│           ├── conscientiousness/
│           ├── extraversion/
│           ├── agreeableness/
│           └── neuroticism/
├── tests/
├── configs/
├── notebooks/
└── docs/
```

### Core Implementation Example
```python
# src/models/personality_analyzer.py
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from typing import Dict, List, Tuple

class PersonalityAnalyzer:
    def __init__(self, model_name: str = "Minej/bert-base-personality"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.trait_names = ['Extraversion', 'Neuroticism', 'Agreeableness', 'Conscientiousness', 'Openness']
        
    def analyze(self, text: str, min_length: int = 500) -> Dict[str, float]:
        """
        Analyze personality from text input
        
        Args:
            text: Input text (minimum 500 words recommended)
            min_length: Minimum character length for reliable analysis
            
        Returns:
            Dictionary with trait names and normalized scores (0.0-1.0)
        """
        if len(text) < min_length:
            raise ValueError(f"Text too short. Need at least {min_length} characters for reliable analysis.")
            
        # Tokenize and predict
        inputs = self.tokenizer(text, truncation=True, padding=True, 
                               return_tensors="pt", max_length=512)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.sigmoid(outputs.logits).squeeze().numpy()
        
        # Convert to trait scores
        results = {}
        for trait, score in zip(self.trait_names, probabilities):
            results[trait] = float(score)
            
        return results
    
    def get_trait_level(self, score: float) -> str:
        """Convert numerical score to categorical level"""
        if score < 0.33:
            return "Low"
        elif score < 0.67:
            return "Medium"
        else:
            return "High"
    
    def analyze_with_levels(self, text: str) -> Dict[str, Dict[str, any]]:
        """Analyze personality and return both scores and levels"""
        scores = self.analyze(text)
        results = {}
        
        for trait, score in scores.items():
            results[trait] = {
                'score': score,
                'level': self.get_trait_level(score),
                'percentile': int(score * 100)
            }
            
        return results
```

---

## Artwork Correlation System

### Trait-to-Image Mapping Structure

Each personality trait will have **3 intensity levels** with corresponding artwork:

#### HEXACO Model Artwork Requirements

**Total Images Needed: 18 images**
- 6 traits × 3 levels = 18 images

#### Big Five Model Artwork Requirements  

**Total Images Needed: 15 images**
- 5 traits × 3 levels = 15 images

#### Combined Implementation: 33 images total

### Detailed Trait Descriptions for Artwork

#### HEXACO Traits

##### 1. Honesty-Humility (H)
- **Low (0.0-0.33):** 
  - **Characteristics:** Manipulative, greedy, entitled, boastful
  - **Visual Concepts:** Dark corporate suits, luxury excess, mirrors reflecting multiple selves, golden crowns with tarnish, scales tipped unfairly
  - **Color Palette:** Dark golds, deep purples, black, metallic silver
  - **Symbols:** Broken scales, coins, masks, thorns

- **Medium (0.34-0.66):**
  - **Characteristics:** Balanced fairness, moderate modesty, occasional self-interest
  - **Visual Concepts:** Balanced scales, handshake, simple clothing, neutral expressions, everyday settings
  - **Color Palette:** Earth tones, soft browns, muted blues, gentle greens
  - **Symbols:** Equal signs, handshakes, simple homes, balanced objects

- **High (0.67-1.0):**
  - **Characteristics:** Sincere, fair, modest, genuine, altruistic
  - **Visual Concepts:** Open hands giving, simple living, humble postures, helping others, natural settings
  - **Color Palette:** Pure whites, soft pastels, natural greens, warm earth tones
  - **Symbols:** Open palms, hearts, simple circles, growing plants

##### 2. Emotionality (E)
- **Low (0.0-0.33):**
  - **Characteristics:** Fearless, independent, tough, emotionally detached
  - **Visual Concepts:** Mountain climbing, solo adventures, calm in storms, steel structures, lone wolf imagery
  - **Color Palette:** Cool grays, steely blues, sharp whites, minimal color
  - **Symbols:** Mountains, steel beams, single figures, geometric shapes

- **Medium (0.34-0.66):**
  - **Characteristics:** Balanced emotional responses, moderate sensitivity
  - **Visual Concepts:** Group activities, supportive friends, gentle weather, comfortable homes
  - **Color Palette:** Warm neutrals, soft blues, gentle yellows, balanced tones
  - **Symbols:** Small groups, comfortable chairs, gentle waves, balanced scales

- **High (0.67-1.0):**
  - **Characteristics:** Sensitive, anxious, sentimental, dependent, fearful
  - **Visual Concepts:** Embracing figures, cozy interiors, protective elements, soft textures, nurturing scenes
  - **Color Palette:** Warm pinks, soft purples, gentle oranges, comforting blues
  - **Symbols:** Hearts, embraces, soft clouds, protective umbrellas, cocoons

##### 3. eXtraversion (X)
- **Low (0.0-0.33):**
  - **Characteristics:** Shy, quiet, reserved, prefers solitude
  - **Visual Concepts:** Reading alone, quiet libraries, single person in nature, minimalist spaces, introspective poses
  - **Color Palette:** Muted tones, soft grays, pale blues, quiet greens
  - **Symbols:** Books, single chairs, closed doors, peaceful lakes, solo paths

- **Medium (0.34-0.66):**
  - **Characteristics:** Socially balanced, comfortable in small groups
  - **Visual Concepts:** Small gatherings, coffee with friends, balanced social settings, selective social interaction
  - **Color Palette:** Balanced warm and cool tones, moderate saturation
  - **Symbols:** Small circles, casual gatherings, selective doors, moderate crowds

- **High (0.67-1.0):**
  - **Characteristics:** Outgoing, confident, sociable, energetic, bold
  - **Visual Concepts:** Large parties, public speaking, vibrant social scenes, leadership poses, dynamic movement
  - **Color Palette:** Bright reds, vibrant oranges, bold yellows, energetic colors
  - **Symbols:** Spotlights, microphones, large groups, open doors, radiating energy

##### 4. Agreeableness (A)
- **Low (0.0-0.33):**
  - **Characteristics:** Critical, stubborn, demanding, quick to anger
  - **Visual Concepts:** Pointed fingers, stern expressions, rigid postures, competitive scenes, confrontational imagery
  - **Color Palette:** Sharp reds, harsh blacks, stark contrasts, aggressive colors
  - **Symbols:** Pointed arrows, clenched fists, sharp angles, barriers

- **Medium (0.34-0.66):**
  - **Characteristics:** Reasonably cooperative, selective forgiveness, balanced assertiveness
  - **Visual Concepts:** Negotiations, balanced discussions, moderate cooperation, thoughtful expressions
  - **Color Palette:** Balanced colors, moderate contrasts, neutral tones
  - **Symbols:** Handshakes, balanced scales, moderate curves, negotiation tables

- **High (0.67-1.0):**
  - **Characteristics:** Forgiving, gentle, flexible, patient, cooperative
  - **Visual Concepts:** Embracing figures, helping hands, peaceful resolutions, gentle interactions, harmonious groups
  - **Color Palette:** Soft pastels, gentle blues, warm pinks, harmonious colors
  - **Symbols:** Embraces, helping hands, smooth curves, bridges, unity symbols

##### 5. Conscientiousness (C)
- **Low (0.0-0.33):**
  - **Characteristics:** Disorganized, impulsive, careless, procrastinating
  - **Visual Concepts:** Messy desks, scattered papers, rushing figures, unfinished projects, chaotic environments
  - **Color Palette:** Chaotic color mixes, bright distracting colors, scattered patterns
  - **Symbols:** Scattered papers, broken clocks, unfinished puzzles, maze-like paths

- **Medium (0.34-0.66):**
  - **Characteristics:** Moderately organized, generally reliable, balanced planning
  - **Visual Concepts:** Tidy but lived-in spaces, moderate organization, balanced schedules, practical approach
  - **Color Palette:** Organized neutral tones, practical colors, moderate structure
  - **Symbols:** Neat stacks, working clocks, partially completed puzzles, clear paths

- **High (0.67-1.0):**
  - **Characteristics:** Highly organized, diligent, perfectionist, disciplined
  - **Visual Concepts:** Perfectly organized spaces, detailed planning, meticulous attention, structured environments
  - **Color Palette:** Clean whites, organized blues, structured grays, precise colors
  - **Symbols:** Perfect grids, precise clocks, completed puzzles, straight lines

##### 6. Openness (O)
- **Low (0.0-0.33):**
  - **Characteristics:** Conventional, practical, traditional, prefers routine
  - **Visual Concepts:** Traditional settings, familiar objects, routine activities, conventional clothing, stable environments
  - **Color Palette:** Conservative colors, traditional combinations, muted tones
  - **Symbols:** Traditional houses, conventional paths, familiar objects, stable foundations

- **Medium (0.34-0.66):**
  - **Characteristics:** Moderately curious, selective creativity, balanced tradition and innovation
  - **Visual Concepts:** Mix of traditional and modern elements, selective exploration, balanced aesthetics
  - **Color Palette:** Mixed traditional and contemporary colors, moderate variety
  - **Symbols:** Half-open doors, selective paths, balanced designs, moderate variety

- **High (0.67-1.0):**
  - **Characteristics:** Creative, imaginative, curious, unconventional, artistic
  - **Visual Concepts:** Abstract art, imaginative landscapes, creative tools, artistic expressions, innovative designs
  - **Color Palette:** Vibrant creative colors, artistic combinations, imaginative palettes
  - **Symbols:** Paint brushes, open books, creative spirals, artistic tools, infinite symbols

### Image Naming Convention

```
{model}_{trait}_{level}.{ext}

Examples:
- hexaco_honesty_humility_low.png
- hexaco_emotionality_high.png
- bigfive_openness_medium.png
```

### Artwork Database Structure
```python
# src/visualization/artwork_correlator.py
class ArtworkCorrelator:
    def __init__(self, artwork_base_path: str = "data/artwork/"):
        self.artwork_base_path = artwork_base_path
        self.trait_mappings = {
            'hexaco': ['honesty_humility', 'emotionality', 'extraversion', 
                      'agreeableness', 'conscientiousness', 'openness'],
            'bigfive': ['openness', 'conscientiousness', 'extraversion', 
                       'agreeableness', 'neuroticism']
        }
    
    def get_artwork_path(self, model: str, trait: str, level: str) -> str:
        """Get path to specific artwork file"""
        filename = f"{model}_{trait}_{level}.png"
        return f"{self.artwork_base_path}{model}/{trait}/{filename}"
    
    def correlate_personality_to_artwork(self, personality_results: Dict) -> Dict[str, str]:
        """Map personality analysis results to corresponding artwork paths"""
        artwork_paths = {}
        
        for trait, data in personality_results.items():
            level = data['level'].lower()
            trait_normalized = trait.lower().replace(' ', '_')
            artwork_path = self.get_artwork_path('hexaco', trait_normalized, level)
            artwork_paths[trait] = artwork_path
            
        return artwork_paths
```

---

## Image Generation Specifications

### Midjourney Prompt Template Structure

```
[Base Scene Description] + [Personality Trait Characteristic] + [Visual Style] + [Color Palette] + [Symbols/Elements] --style raw --ar 16:9 --v 6
```

### Example Prompts for Each Trait Level

#### Honesty-Humility Low:
```
Corporate executive in dark suit surrounded by golden luxury items and mirrors reflecting multiple deceptions, manipulative hand gestures, dark corporate office with tarnished golden accents, deep purples and blacks, broken scales and coins scattered around, photorealistic style --style raw --ar 16:9 --v 6
```

#### Emotionality High:
```
Gentle figure embracing someone in soft cozy interior, warm protective atmosphere, soft textures and nurturing elements, warm pinks and gentle oranges, hearts and embracing symbols, soft lighting, emotional warmth, photorealistic style --style raw --ar 16:9 --v 6
```

#### eXtraversion High:
```
Confident person speaking to large crowd with dynamic energy, vibrant social scene, leadership pose with radiating energy, bright reds and vibrant oranges, spotlight and microphone elements, dynamic movement, photorealistic style --style raw --ar 16:9 --v 6
```

### Style Reference Consistency

Use a consistent style reference across all images:
```
--sref [your_style_reference_url] --sw 50
```

This ensures visual consistency while allowing for personality-specific variations.

---

## Complete Source Citations

### Academic Papers and Research

1. **Lee, K., & Ashton, M. C. (2018).** Psychometric properties of the HEXACO-100. *Assessment*, 25(5), 543-556. https://doi.org/10.1177/1073191116659134

2. **Husain, S. F., et al. (2025).** Reliability generalization meta-analysis of the internal consistency of the Big Five Inventory. *BMC Psychology*, 13(1), 1-15. https://bmcpsychology.biomedcentral.com/articles/10.1186/s40359-024-02271-x

3. **Zhang, L., et al. (2023).** PsyAttention: Psychological Attention Model for Personality Detection. *EMNLP 2023 Findings*. https://aclanthology.org/2023.findings-emnlp.222/

4. **Kerz, E., et al. (2022).** Pushing on Personality Detection from Verbal Behavior: A Transformer Meets Text Contours of Psycholinguistic Features. *arXiv preprint*. https://arxiv.org/abs/2204.04629

5. **Ahmad, J., et al. (2021).** Text based personality prediction from multiple social media data sources using pre-trained language model and model averaging. *Journal of Big Data*, 8(1), 1-20. https://journalofbigdata.springeropen.com/articles/10.1186/s40537-021-00459-1

### Technical Resources

1. **Hugging Face - bert-base-personality:** https://huggingface.co/Minej/bert-base-personality
2. **SenticNet Personality Detection:** https://github.com/SenticNet/personality-detection
3. **DeepPersonality Benchmark:** https://github.com/liaorongfan/DeepPersonality
4. **Personality Prediction Pipeline:** https://github.com/yashsmehta/personality-prediction

### APIs and Commercial Services

1. **Receptiviti API Documentation:** https://docs.receptiviti.com/frameworks/personality-big-5
2. **Apply Magic Sauce:** https://applymagicsauce.com/about-us
3. **Crystal Knows API:** https://www.crystalknows.com/app/developers

### Datasets

1. **Big Five Personality Test (Kaggle):** https://www.kaggle.com/datasets/tunguz/big-five-personality-test
2. **Open Psychometrics Raw Data:** https://openpsychometrics.org/_rawdata/
3. **PANDORA Dataset Reference:** https://arxiv.org/html/2409.19723

---

## Development Instructions

### Phase 1: Environment Setup
```bash
# Create project directory
mkdir personality-ai-project
cd personality-ai-project

# Set up Python environment
python -m venv personality-env
source personality-env/bin/activate  # Linux/Mac
# personality-env\Scripts\activate  # Windows

# Install requirements
pip install transformers torch pandas numpy scikit-learn fastapi uvicorn python-multipart Pillow matplotlib seaborn
```

### Phase 2: Basic Implementation
1. Create the project structure as outlined above
2. Implement the PersonalityAnalyzer class
3. Set up the artwork correlation system
4. Create basic FastAPI endpoints

### Phase 3: Artwork Integration
1. Generate artwork using the specifications above
2. Organize artwork files according to the naming convention
3. Implement artwork correlation logic
4. Test visual-personality mappings

### Phase 4: Validation and Testing
1. Validate model accuracy on test datasets
2. Ensure artwork correlations are meaningful
3. Test with various text inputs
4. Document performance metrics

### Phase 5: Deployment
1. Containerize with Docker
2. Set up CI/CD pipeline
3. Deploy API endpoints
4. Create user documentation

## Usage Example

```python
from src.models.personality_analyzer import PersonalityAnalyzer
from src.visualization.artwork_correlator import ArtworkCorrelator

# Initialize components
analyzer = PersonalityAnalyzer()
artwork_correlator = ArtworkCorrelator()

# Analyze personality from text
text = "Your input text here (minimum 500 characters recommended)"
personality_results = analyzer.analyze_with_levels(text)

# Get corresponding artwork
artwork_paths = artwork_correlator.correlate_personality_to_artwork(personality_results)

# Results include both personality scores and visual correlations
for trait, data in personality_results.items():
    print(f"{trait}: {data['level']} ({data['percentile']}%)")
    print(f"Artwork: {artwork_paths[trait]}")
```

This complete package provides everything needed to implement a scientifically robust personality assessment AI system with visual correlation capabilities.