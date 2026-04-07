# Segmentação de Água em Imagens de Satélite

Solução para a trilha de segmentação semântica da **2026 ITU · Ingenuity Cup AI and Space Computing Challenge**, cujo objetivo era identificar a classe água em imagens de satélite de alta resolução do sensor Gaofen-2.

**Autor:** Luiz Felipe Castro — luiz.castro@usp.br

---

## O problema

O dataset GID (Gaofen Image Dataset) contém imagens RGB de satélite com máscaras de segmentação multiclasse. A tarefa era segmentar especificamente a **classe água** (rios, lagos e reservatórios), produzindo máscaras binárias para as imagens de teste.

O principal desafio foi o forte **desbalanceamento de classes**: a água ocupa uma fração pequena da maioria das imagens, especialmente em rios finos. A métrica oficial da competição era o **Kappa de Cohen**, que penaliza modelos que ignoram a classe minoritária.

---

## Abordagem

```
Imagens RGB (512×512) + máscaras GID
         ↓
Split estratificado por presença de água (80/20)
         ↓
Augmentation agressiva (crop, flip, distorções, dropout)
         ↓
UNet++ · EfficientNet-b1 · atenção scSE
         ↓
Loss combinada: FocalTversky + BCE ponderada + Lovász
         ↓
Validação temporal com Kappa de Cohen
         ↓
Submissão com TTA (4 flips)
```

## Decisões técnicas

**Arquitetura — UNet++ com EfficientNet-b1**  
O UNet++ usa conexões densas entre encoder e decoder para capturar estruturas em múltiplas escalas, importante para detectar tanto lagos grandes quanto rios finos. A atenção scSE recalibra as features espacialmente e por canal. O EfficientNet-b1 foi escolhido sobre o b3 por limitação de VRAM da GPU P100 do Kaggle (16GB).

**Função de perda combinada**  
- *FocalTversky (60%):* penaliza mais falsos negativos, com alpha=0.7 e gamma=1.5 para focar nos exemplos difíceis  
- *BCE ponderada (20%):* pos_weight estimado dinamicamente a partir do desbalanceamento real do dataset  
- *Lovász (20%):* aproximação diferenciável do IoU, melhora a qualidade das bordas  

**Gradient accumulation**  
Batch size 2 com acumulação de 8 passos, simulando batch efetivo de 16 sem estourar a VRAM.

**Checkpoint entre sessões**  
O Kaggle limita sessões a ~12h. O treinamento foi retomado entre sessões via checkpoint salvo no dataset do Kaggle.

**TTA na submissão**  
Média das probabilidades com a imagem original e três versões espelhadas (flip H, flip V, flip HV), reduzindo a variância sem custo de treinamento.

---

## Estrutura do repositório

```
water_segmentation/
├── notebooks/
│   ├── 01_exploracao_tentativas.ipynb   # Inspeção dos dados e tentativas descartadas
│   └── 02_pipeline_final.ipynb          # Pipeline completo de treino e submissão
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Como reproduzir

> Os dados são da competição e não podem ser redistribuídos. Para reproduzir, é necessário ter acesso ao dataset GID via [zero2x](https://spaceaichallenge.zero2x.org).

```bash
git clone https://github.com/seu-usuario/water_segmentation.git
cd water_segmentation
pip install -r requirements.txt
```

Ajuste os caminhos `IMG_FOLDERS`, `LBL_DIR` e `TEST_DIR` no notebook `02_pipeline_final.ipynb` para apontar para os dados locais, depois execute as células em ordem.

---

## Tecnologias

- **PyTorch** — treinamento e inferência
- **segmentation-models-pytorch** — UNet++, losses (Lovász)
- **Albumentations** — augmentation
- **OpenCV** — leitura e processamento de imagens
