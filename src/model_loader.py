import degirum as dg

def load_model(model_name, inference_host_address, zoo_url, overlay_color=None, output_use_regular_nms=False, output_confidence_threshold=0.1):
    
    try:
        model = dg.load_model(
            model_name=model_name,
            inference_host_address=inference_host_address,
            zoo_url=zoo_url,
            overlay_color=overlay_color,
            output_use_regular_nms=output_use_regular_nms,
            output_confidence_threshold=output_confidence_threshold
        )
        return model
    except Exception as e:
        logging.error(f"Failed to load model '{model_name}': {e}")
        raise