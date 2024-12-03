def load_model(
    model_path: str,
    api_key: str = 'yz',
):
    if 'llama' in model_path.lower():
        from load_models.load_llama import load_llama, call_llama
        model = load_llama(model_path, api_key)
        return lambda *args, **kwargs: call_llama(model, *args, **kwargs)
    elif 'claude' in model_path.lower():
        from load_models.load_claude import load_claude, call_claude
        model = load_claude(model_path, api_key)
        return lambda *args, **kwargs: call_claude(model, *args, **kwargs)
    elif 'gpt' in model_path.lower():
        from load_models.load_gpt import load_gpt, call_gpt
        model = load_gpt(model_path, api_key)
        return lambda *args, **kwargs: call_gpt(model, *args, **kwargs)
    elif 'gemini' in model_path.lower():
        from load_models.load_gemini import load_gemini, call_gemini
        model = load_gemini(model_path, api_key)
        return lambda *args, **kwargs: call_gemini(model, *args, **kwargs)
    elif 'qwen' in model_path.lower():
        from load_models.load_qwen import load_qwen, call_qwen
        model = load_qwen(model_path)
        return lambda *args, **kwargs: call_qwen(model, *args, **kwargs)
    elif 'mistral' in model_path.lower() or 'mixtral' in model_path.lower():
        from load_models.load_mistral import load_mistral, call_mistral
        model = load_mistral(model_path)
        return lambda *args, **kwargs: call_mistral(model, *args, **kwargs)
    elif 'pixtral' in model_path.lower():
        from load_models.load_pixtral import load_pixtral, call_pixtral
        model = load_pixtral(model_path)
        return lambda *args, **kwargs: call_pixtral(model, *args, **kwargs)
    elif 'stable' in model_path.lower():
        from load_models.load_sd import load_sd, call_sd
        model = load_sd(model_path)
        return lambda *args, **kwargs: call_sd(model, *args, **kwargs)
    else:
        raise ValueError(f"Model {model_path} not found")