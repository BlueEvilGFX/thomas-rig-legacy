import bpy
from bpy.props import StringProperty
import os
import requests
import json
import base64

from .. import utils
from .. import constants


class THOMAS_RIG_SKIN_DOWNLOAD(bpy.types.Operator):
    bl_idname = "thomasriglegacy.downloadskin"
    bl_label = ""
    bl_description = "downloads the minecraft skin by user name"

    user_name : StringProperty() # type: ignore

    @classmethod
    def poll(cls, context):
        return bpy.app.online_access

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Please enter the username from which you want to get the skin.", icon='FILE_TEXT')
        layout.prop(self, 'user_name')

    def execute(self, context):
        # download not successfull
        if not self.download_init():
            return {'CANCELLED'}
        
        rig = utils.get_rig() 
        context.view_layer.objects.active = rig

        # set skin and pack texture
        mat_obj = utils.get_mat_object(rig)
        mat = mat_obj.material_slots[0].material
        skin_img = mat.node_tree.nodes['Skin'].image
        skin_img.filepath = self.save_location
        skin_img.pack()

        # check for alex arms
        rig.pose.bones["Main_Properties"]["Slim main"] = self.alex_arms

        self.report({'INFO'}, 'Skin has been downloaded and changed!')
        return {'FINISHED'}
        
    def download_init(self) -> bool:
        self.player_uuid = self.fetch_UUID()
        if self.player_uuid is None:
            return False # player name not found
        
        self.skin_value = self.fetch_skin_value()
        self.skin_url, self.alex_arms = self.fetch_skin_url()
        self.save_location = self.download_skin()
        return (self.player_uuid is not None and self.save_location is not None)

    def fetch_UUID(self):
        try:
            response = requests.get(constants.UUID_URL + self.user_name)
            data = response.json()
            if "errorMessage" in data:
                self.report({'ERROR'}, data["errorMessage"])
                return None
            self.user_name = data.get('name')
            return data.get('id')
        except requests.exceptions.RequestException as e:
            self.report({'ERROR'}, f"Something went wrong with the request {e}")

    def fetch_skin_value(self):
        try:
            response = requests.get(constants.SKIN_URL + self.player_uuid)
            data = response.json()
            if "errorMessage" in data:
                self.report({'ERROR'}, data["errorMessage"])
                return None
            return data.get('properties')[0].get('value')
        except requests.exceptions.RequestException as e:
            self.report({'ERROR'}, f"Something went wrong with the request {e}")

    def fetch_skin_url(self):
        byte_code = base64.b64decode(self.skin_value)
        string_code = str(byte_code, 'utf-8')
        data = json.loads(string_code)
        skin_url = data.get('textures').get('SKIN').get('url')
        alex_arms = data.get('textures').get('SKIN').get('metadata', {}).get('model') == 'slim'
        return skin_url, alex_arms
    
    def download_skin(self):
        try:
            response = requests.get(self.skin_url, stream=True)
            response.raise_for_status()

            # saves skin to temp folder
            temp_dir = bpy.app.tempdir
            save_location = os.path.join(temp_dir, f"{self.user_name}.png")
            with open(save_location, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192): 
                    file.write(chunk)
            return save_location
        except requests.exceptions.RequestException as e:
            self.report({'ERROR'}, f"An error occurred while downloading the skin: {e}")
            return None