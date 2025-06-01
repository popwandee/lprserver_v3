import degirum as dg
import degirum_tools

hailo_model_zoo = dg.connect(
    inference_host_address='@local',
    zoo_url='resources'    
)
print(hailo_model_zoo.list_models())
