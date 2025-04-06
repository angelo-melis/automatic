import os
import time
from modules import shared, errors, sd_models, sd_checkpoint, model_quant, devices
from modules.video_models import models_def, video_utils, video_vae, video_overrides, video_cache


loaded_model = None
debug = shared.log.trace if os.environ.get('SD_VIDEO_DEBUG', None) is not None else lambda *args, **kwargs: None


def load_model(selected: models_def.Model):
    if selected is None:
        return ''
    global loaded_model # pylint: disable=global-statement
    if loaded_model == selected.name:
        return ''
    sd_models.unload_model_weights()
    t0 = time.time()

    video_cache.apply_teacache_patch(selected.dit_cls)

    # text encoder
    try:
        quant_args = model_quant.create_config(module='TE')
        debug(f'Video load: module=te repo="{selected.te or selected.repo}" folder="{selected.te_folder}" cls={selected.te_cls.__name__} quant={video_utils.get_quant(quant_args)}')
        text_encoder = selected.te_cls.from_pretrained(
            pretrained_model_name_or_path=selected.te or selected.repo,
            subfolder=selected.te_folder,
            cache_dir=shared.opts.hfcache_dir,
            torch_dtype=devices.dtype,
            **quant_args
        )
    except Exception as e:
        shared.log.error(f'video load: module=te cls={selected.te_cls.__name__} {e}')
        errors.display(e, 'video')
        text_encoder = None

    # transformer
    try:
        quant_args = model_quant.create_config(module='Video')
        debug(f'Video load: module=transformer repo="{selected.dit or selected.repo}" folder="{selected.dit_folder}" cls={selected.dit_cls.__name__} quant={video_utils.get_quant(quant_args)}')
        transformer = selected.dit_cls.from_pretrained(
            pretrained_model_name_or_path=selected.dit or selected.repo,
            subfolder=selected.dit_folder,
            torch_dtype=devices.dtype,
            cache_dir=shared.opts.hfcache_dir,
            **quant_args
        )
    except Exception as e:
        shared.log.error(f'video load: module=transformer cls={selected.dit_cls.__name__} {e}')
        errors.display(e, 'video')
        transformer = None

    # overrides
    kwargs = video_overrides.load_override(selected)

    # model
    try:
        debug(f'Video load: module=pipe repo="{selected.repo}" cls={selected.repo_cls.__name__}')
        shared.sd_model = selected.repo_cls.from_pretrained(
            pretrained_model_name_or_path=selected.repo,
            transformer=transformer,
            text_encoder=text_encoder,
            cache_dir=shared.opts.hfcache_dir,
            torch_dtype=devices.dtype,
            **kwargs,
        )
    except Exception as e:
        shared.log.error(f'video load: module=pipe repo="{selected.repo}" cls={selected.repo_cls.__name__} {e}')
        errors.display(e, 'video')

    t1 = time.time()
    shared.sd_model.sd_checkpoint_info = sd_checkpoint.CheckpointInfo(selected.repo)
    shared.sd_model.sd_model_hash = None
    sd_models.set_diffuser_options(shared.sd_model)
    if selected.vae_hijack and hasattr(shared.sd_model.vae, 'decode'):
        shared.sd_model.vae.orig_decode = shared.sd_model.vae.decode
        shared.sd_model.vae.decode = video_vae.hijack_vae_decode
        shared.sd_model.vae.orig_encode = shared.sd_model.vae.encode
        shared.sd_model.vae.encode = video_vae.hijack_vae_encode
    if selected.te_hijack and hasattr(shared.sd_model, 'encode_prompt'):
        shared.sd_model.orig_encode_prompt = shared.sd_model.encode_prompt
        shared.sd_model.encode_prompt = video_utils.hijack_encode_prompt
    if selected.image_hijack and hasattr(shared.sd_model, 'encode_image'):
        shared.sd_model.orig_encode_image = shared.sd_model.encode_image
        shared.sd_model.encode_image = video_utils.hijack_encode_image
    if hasattr(shared.sd_model.vae, 'enable_slicing'):
        shared.sd_model.vae.enable_slicing()
    loaded_model = selected.name
    msg = f'Video load: cls={shared.sd_model.__class__.__name__} model="{selected.name}" time={t1-t0:.2f}'
    shared.log.info(msg)
    return msg
