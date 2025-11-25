# 🧬 Dismorphology Atlas

Atlas interactivo de terminología dismorfológica basado en "Elements of Morphology" - Standard Terminology.

## 📋 Descripción

Este proyecto contiene una extracción completa y organizada de términos dismorfológicos de los documentos "Elements of Morphology" publicados en American Journal of Medical Genetics. Incluye **128 términos médicos** con sus definiciones, **694 imágenes PNG** de alta calidad extraídas automáticamente, y una **aplicación web interactiva** con diseño moderno para explorar el contenido médico.

### 🆕 Nuevas Características (Noviembre 2025)
- ✅ **Extracción automatizada completa** de 22 documentos PDF
- ✅ **Mapeo inteligente término-imagen** basado en análisis de captions
- ✅ **190 relaciones precisas** entre términos e imágenes  
- ✅ **Diseño de dos columnas** que da protagonismo a las imágenes
- ✅ **Modal de imagen mejorado** con zoom 2x y controles intuitivos

## ✨ Características

- 🔍 **128 términos dismorfológicos** extraídos y verificados con definiciones completas
- 🖼️ **694 imágenes PNG** de alta calidad extraídas automáticamente de los PDFs
- 🔗 **190 relaciones término-imagen** creadas mediante análisis inteligente de captions
- 📚 **7 categorías anatómicas** organizadas (ear, hands_feet, head_face, lips_mouth, etc.)
- 🌐 **Aplicación web interactiva** con búsqueda en tiempo real y diseño de dos columnas
- 📊 **Datos en formato JSON** estructurados y fáciles de integrar
- 🎨 **Interfaz moderna y responsive** optimizada para visualización médica
- 🐳 **Contenedorización Docker** para despliegue sencillo

## 🚀 Inicio Rápido

### Opción 1: Docker (Recomendado) 🐳

La forma más rápida de ejecutar el proyecto:

```bash
# Usando el script automático
./start-docker.sh

# O manualmente
docker-compose up -d --build
```

La aplicación estará disponible en: **http://localhost:8888**

Ver [DOCKER_README.md](DOCKER_README.md) para más detalles.

### Opción 2: Python Simple Server

```bash
# Con Python 3
python3 -m http.server 8000
# Abre: http://localhost:8000

# Con Python 2
python -m SimpleHTTPServer 8000
```

### Opción 3: Abrir Directamente

Doble clic en `index.html` (funciona en la mayoría de navegadores modernos)

### Usar los Datos

```javascript
// Cargar todos los términos
fetch('data/organized/morphology_terms.json')
  .then(r => r.json())
  .then(terms => {
    console.log(`Total términos: ${terms.length}`);
    // terms es un array de 781 términos
  });

// Cargar términos por categoría
fetch('data/organized/terms_by_category.json')
  .then(r => r.json())
  .then(categories => {
    console.log(categories.ear);        // 101 términos del oído
    console.log(categories.hands_feet); // 118 términos de manos/pies
  });
```

## 📂 Estructura del Proyecto

```
morphology-atlas/
│
├── 📄 index.html                    # Aplicación web interactiva
├── 📄 README.md                     # Este archivo
├── 📄 INICIO_RAPIDO.md              # Guía de inicio rápido
├── 📄 RESUMEN_FINAL.md              # Resumen detallado del proyecto
├── 📄 README_EXTRACTION.md          # Documentación técnica
│
├── 📂 pdfs/                         # PDFs originales (22 archivos)
│   └── *.pdf
│
├── 📂 data/                         # Textos extraídos
│   ├── *.txt                        # 22 archivos de texto
│   ├── extraction_metadata.json     # Metadata de extracción
│   │
│   └── 📂 organized/                # Datos organizados
│       ├── morphology_terms.json        # 781 términos completos
│       ├── terms_by_category.json       # Términos por categoría
│       ├── terms_index.json             # Índice de términos
│       ├── content_by_category.json     # Contenido organizado
│       ├── summary.json                 # Resumen estadístico
│       └── images_catalog.json          # Catálogo de imágenes
│
├── 📂 images/                       # 1,138 imágenes PNG
│   └── *.png
│
└── 📂 scripts/                      # Scripts de procesamiento
    ├── extract_pdfs.py              # Extractor de PDFs
    ├── extract_terms.py             # Extractor de términos
    ├── organize_content.py          # Organizador de contenido
    └── create_sample.py             # Creador de ejemplos
```

## 📊 Categorías Anatómicas

| Categoría | Términos | Imágenes | Emoji |
|-----------|----------|----------|-------|
| Manos y Pies | 30 | 103 | ✋ |
| Cabeza y Cara | 27 | 75 | 👤 |
| Nariz y Filtrum | 17 | 55 | 👃 |
| Labios y Boca | 17 | 58 | 👄 |
| Oído | 15 | 76 | 👂 |
| General | 13 | 52 | 📚 |
| Periorbital | 9 | 41 | 👁️ |

### 🔗 Mapeo Término-Imagen
- **95 términos** (74%) tienen imágenes relacionadas
- **190 relaciones** término-imagen establecidas
- **Análisis automático** de captions para crear asociaciones precisas

## 💻 Formato de los Datos

### Estructura de un Término

```json
{
  "term": "Antihelix",
  "definition": "A Y-shaped curved cartilaginous ridge arising from the antitragus...",
  "category": "ear",
  "document": "Hunter et al. - 2009 - Elements of morphology Standard terminology for the ear",
  "source": "elements_of_morphology_standard_terminology_for_the_ear.txt"
}
```

### Categorías Disponibles en JSON

```json
{
  "ear": [
    { "term": "Antihelix", "definition": "...", ... },
    { "term": "Tragus", "definition": "...", ... }
  ],
  "hands_feet": [
    { "term": "Brachydactyly", "definition": "...", ... }
  ]
}
```

## 🛠️ Scripts Disponibles

### Extraer Contenido de PDFs

```bash
python3 extract_pdfs.py
```

Extrae texto e imágenes de todos los PDFs en la carpeta `pdfs/`.

### Organizar Contenido por Categorías

```bash
python3 organize_content.py
```

Organiza el contenido extraído en categorías anatómicas.

### Extraer Términos Morfológicos

```bash
python3 extract_terms.py
```

Extrae términos con definiciones usando reconocimiento de patrones inteligente.

## 🎨 Características de la Aplicación Web

### 🖥️ Interfaz Principal
- ✅ **Dashboard con estadísticas** en tiempo real
- ✅ **Búsqueda instantánea** de términos con autocompletado
- ✅ **Vista de categorías** organizadas por región anatómica
- ✅ **Acordeón interactivo** para navegación intuitiva
- ✅ **Filtrado por categoría** con contadores dinámicos

### 📋 Modal de Término (Diseño de Dos Columnas)
- ✅ **Columna de texto** (40%): Definición, metadatos y referencias
- ✅ **Columna de imágenes** (60%): Galería visual prominente
- ✅ **Scroll independiente** en cada columna
- ✅ **Relaciones término-imagen** basadas en análisis de captions

### 🖼️ Visor de Imágenes
- ✅ **Zoom 2x** para ver detalles médicos
- ✅ **Controles intuitivos** (click, ESC, botón X)
- ✅ **Captions originales** de los documentos fuente
- ✅ **Navegación fluida** entre imágenes relacionadas

### 📱 Diseño Responsivo
- ✅ **Adaptación automática** a tablets y móviles  
- ✅ **Columnas apilables** en pantallas pequeñas
- ✅ **Grid flexible** de imágenes por dispositivo
- ✅ **Navegación táctil** optimizada

## 📖 Documentación

- **[INICIO_RAPIDO.md](INICIO_RAPIDO.md)** - Guía de inicio rápido
- **[RESUMEN_FINAL.md](RESUMEN_FINAL.md)** - Resumen detallado con ejemplos
- **[README_EXTRACTION.md](README_EXTRACTION.md)** - Documentación técnica completa

## 🔧 Requisitos

### Para Docker (Recomendado)
- Docker >= 20.10
- docker-compose >= 1.29

### Para desarrollo local
- Python 3.6+ (opcional, solo para scripts de procesamiento)
- Navegador web moderno
- PyMuPDF (solo para re-procesar PDFs)

```bash
pip install PyMuPDF
```

## 📚 Fuente de los Datos

Los datos provienen de la serie "Elements of Morphology" publicada en:
- American Journal of Medical Genetics Part A
- Autores: Allanson JE, Biesecker LG, Carey JC, Hennekam RCM, Hunter A, et al.
- Años: 2009-2019

## 📄 Licencia

Este proyecto organiza y presenta contenido académico publicado bajo licencia Creative Commons. El contenido original pertenece a sus respectivos autores y editores.

## ✅ Estado del Proyecto

- [x] Extracción de PDFs completada
- [x] Organización de contenido completada
- [x] Extracción inteligente de términos completada
- [x] Aplicación web interactiva completada
- [x] Documentación completada
- [x] Manejo de formato de dos columnas
- [x] Limpieza y deduplicación de términos

## 🎯 Uso Recomendado

Este atlas de dismorfología es ideal para:
- 👨‍⚕️ Estudiantes de medicina
- 👨‍🔬 Genetistas clínicos
- 👨‍💻 Desarrolladores de aplicaciones médicas
- 📚 Investigadores en dismorfología
- 🏥 Profesionales de la salud
- 🧬 Especialistas en genética médica

## 🤝 Contribuciones

Para mejorar el proyecto:
1. Revisa los términos extraídos en `data/organized/morphology_terms.json`
2. Verifica la calidad de las imágenes en `images/`
3. Prueba la aplicación web en `index.html`
4. Sugiere mejoras o reporta problemas

---

**Desarrollado con** ❤️ **para la comunidad médica y científica**
