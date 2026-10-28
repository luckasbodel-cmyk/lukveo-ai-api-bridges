# LUKVEO AI API Bridges — démonstration de code

Extraits **réels** de modules Python développés au cours du prototype personnel LUKVEO AI PRO, présentés séparément pour une revue technique. Il ne s’agit **ni** de l’application JARVIS complète, **ni** d’un produit commercial déployé.

## Ce que montre le code

- `api/gemini_bridge.py` : validation de modèle et de message, appel au SDK `google-genai`, gestion des erreurs et collecte facultative de statistiques.
- `api/lukveo_groq_bridge.py` : appel HTTP JSON vers l'API Groq (bibliothèque `requests`), sélection contrôlée des modèles, gestion des réponses HTTP.
- `api/lukveo_token_usage.py` : journalisation facultative de compteurs d’usage dans une base SQLite locale, sans enregistrer les prompts ni les clés.

## Tester sans clé, sans réseau

```bash
python demo_validation.py
```

Ce test vérifie les mécanismes de validation ; **il ne prouve pas** qu'un appel aux fournisseurs réussit. Pour tester de véritables appels, installer `requirements.txt`, créer localement un `.env` **non publié** à partir de `.env.example` ou définir les variables d’environnement requises, puis intégrer les fonctions dans une application adaptée. **Attention :** `gemini_bridge.py` lit la clé Gemini uniquement depuis l'environnement et `lukveo_groq_bridge.py` peut lire le `.env` local.

## Limites et transparence

- Les identifiants de modèles sont ceux du projet source : leur disponibilité réelle et leur facturation doivent être vérifiées chez les fournisseurs.
- Aucun accès navigateur, interface JARVIS ou serveur web n’est fourni.
- Le traitement des erreurs et les dépendances demanderaient des tests supplémentaires avant production.
- La contribution est présentée comme **projet personnel de formation**, sans prétendre à une expérience professionnelle chez un client.

**Sécurité :** ne jamais publier `.env`, clés, bases SQLite réelles, historiques ou données clients.
