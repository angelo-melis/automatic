# TODO

Main ToDo list can be found at [GitHub projects](https://github.com/users/vladmandic/projects)

## Current

- ModernUI for custom model loader  
- ModernUI for history tab  

### Issues/Limitations

N/A

## Future Candidates

- IPAdapter: negative guidance: <https://github.com/huggingface/diffusers/discussions/7167>  
- Control: API enhance scripts compatibility  
- Video: add generate context menu  
- Video: API support  
- Video: STG: <https://github.com/huggingface/diffusers/blob/main/examples/community/README.md#spatiotemporal-skip-guidance>  
- Video: SmoothCache: https://github.com/huggingface/diffusers/issues/11135  

## Code TODO

> pnpm lint | grep W0511 | awk -F'TODO ' '{print "- "$NF}' | sed 's/ (fixme)//g'
 
- control: support scripts via api
- fc: autodetect distilled based on model
- fc: autodetect tensor format based on model
- hidream: pack latents for remote vae
- hypertile: vae breaks when using non-standard sizes
- infotext: handle using regex instead
- install: enable ROCm for windows when available
- loader: load receipe
- loader: save receipe
- lora: add other quantization types
- lora: maybe force imediate quantization
- lora: add t5 key support for sd35/f16
- lora: support pre-quantized flux
- model load: force-reloading entire model as loading transformers only leads to massive memory usage
- model loader: implement model in-memory caching
- modernui: monkey-patch for missing tabs.select event
- nunchaku: batch support
- nunchaku: cache-dir for transformer and t5 loader
- processing: remove duplicate mask params
- resize image: enable full VAE mode for resize-latent
  