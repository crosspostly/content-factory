# Qwen Setup - 3 Easy Steps 🚀

## ✅ Они уже У ТЕБЯ!

Ключи из Qwen Code CLI вытащены:

```json
{
  "access_token": "MAuuK24ct034RejWX7W_FuET6r1nsQ1iq9uzV5AXIMPC8iuPoEuoZNah74vdfkxmRINIJdhmjN47lzaheCDLvQ",
  "refresh_token": "1dxcdJ3uDRIPl5F0EEaB0un0lS1-dkEby3Hqb1z1qdSn4HWeUoa23jZKOkvJ_Bg4a7ijeR6TBOznPdJd1c1Wmg",
  "token_type": "Bearer",
  "resource_url": "portal.qwen.ai",
  "expiry_date": 1765543004617
}
```

---

## Step 1: Гитхаб Settings

Открыть:
```
https://github.com/crosspostly/content-factory/settings/secrets/actions
```

---

## Step 2: Добавить Secret

Кнопка **"New repository secret"**

**Name:**
```
QWEN_ACCESS_TOKEN
```

**Value:**
```
MAuuK24ct034RejWX7W_FuET6r1nsQ1iq9uzV5AXIMPC8iuPoEuoZNah74vdfkxmRINIJdhmjN47lzaheCDLvQ
```

🌟 **Click "Add secret"**

---

## Step 3: Менять Master Config

Открыть: `.github/auto-fix-master-config.yml`

Дит что используется:

```yaml
ai_models:
  primary: 'gemini'  # ← Это меняй!
```

Поменять на:

```yaml
ai_models:
  primary: 'qwen'  # Команда доктора! 💫
```

---

## 🚀 Готово!

Теперь следующая failure будет анализирована **Qwen**!

---

## 💳 Options

### Только Qwen:
```yaml
ai_models:
  primary: 'qwen'
```

### Только Gemini:
```yaml
ai_models:
  primary: 'gemini'
```

### Обе модели (Dual Mode):
```yaml
ai_models:
  primary: 'dual'
  
  dual:
    enabled: true
    strategy: 'compare'  # Сравни и выбери лучшее
```

---

## 🔍 Проверить что работает

### GitHub → Actions → "Test Auto-Fix Trigger" → Run workflow

Он выберет модель из master-config и справится с ней.

Если primary = 'qwen' → использует твой QWEN_ACCESS_TOKEN 

✅ **Done!**

---

## ⚠️ Важно

- Токен вынесен через ✅ дни (с 13 декабря 2025)
- После этого ты скопируешь refresh_token и обновишь
- дит установить `QWEN_REFRESH_TOKEN` если хочешь авторефреш

---

**Ключи у тебя уже есть! 🚀**
