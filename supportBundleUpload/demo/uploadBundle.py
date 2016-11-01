# coding: utf-8

from __future__ import print_function, unicode_literals
import os
from boxsdk import Client
from boxsdk.exception import BoxAPIException
from boxsdk.object.collaboration import CollaborationRole
from auth import authenticate
from boxsdk import JWTAuth
import shelve
import argparse
import sys
import ConfigParser
import datetime
import time
from pprint import pprint

def get_folder_shared_link(client):
    root_folder = client.folder(folder_id='0')
    collab_folder = root_folder.create_subfolder('shared link folder')
    try:
        print('Folder {0} created'.format(collab_folder.get().name))
        shared_link = collab_folder.get_shared_link()
        print('Got shared link:' + shared_link)
    finally:
        print('Delete folder collab folder succeeded: {0}'.format(collab_folder.delete()))


def upload_file(client):
    root_folder = client.folder(folder_id='0')
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'file.txt')
    a_file = root_folder.upload(file_path, file_name='i-am-a-file.txt')
    try:
        print('{0} uploaded: '.format(a_file.get()['name']))
    except BoxAPIException:
        print('{0} upload failed: '.format(a_file.get()['name']))


def get_events(client):
    print(client.events().get_events(limit=100, stream_position='now'))


def get_latest_stream_position(client):
    print(client.events().get_latest_stream_position())


def long_poll(client):
    print(client.events().long_poll())


def _delete_leftover_group(existing_groups, group_name):
    """
    delete group if it already exists
    """
    existing_group = next((g for g in existing_groups if g.name == group_name), None)
    if existing_group:
        existing_group.delete()

def store_tokens_callback_method(access_token, refresh_token):
    # store the tokens at secure storage (e.g. Keychain)
    d =  shelve.open("db.shlv")
    d["access_token"]=access_token
    d["refresh_token"]=refresh_token
    d.close()
    return

def get_auth():
        
    auth = JWTAuth(
        client_id='37vdfnknzax5htrkiler5xkphbxs6f4s',
        client_secret='pMUwYf2g1iAsvFDnCA08ASa1oHwYj3Ut',
        enterprise_id="849101",
        jwt_key_id='h4qpyf9b',
        rsa_private_key_file_sys_path='private_key.pem',
	rsa_private_key_passphrase=b'datos1234',
    )

    access_token = auth.authenticate_instance()
    client = Client(auth)

    print("Upload authenticated successfully")

    return client

def handle_cli():

    parser = argparse.ArgumentParser(description="Document upload to Box through API")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--setup", action="count", help="Setup the Initial Configuration File (One time operation)")
    group.add_argument("-l", "--logs", action="count", help="Upload Support Bundle")
    group.add_argument("-c", "--callhome", action="count", help="Send Call Home Report")
    args = parser.parse_args()    
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    return args

def gen_config_file():

    # Sample config file
    # [General]
    # Customer-Name = "Home Depot"
    # Datos-Cluster-Name = "HD_Staging"
    # Datos-Cluster-Id = 0
    # Box-User-Login = "venkat.reddimanchu@box.com"
    
    # lets create that config file for next time...
    cfgfile = open("box.cfg",'w')
    
    # add the settings to the structure of the file, and lets write it out...
    Config = ConfigParser.RawConfigParser()
    Config.add_section('General')
    Config.set('General', '#Please do not edit the values below.')
    cust_name = raw_input("Please provide customer name:")
    Config.set('General', 'Customer-Name',cust_name)
    datos_name = raw_input("Please provide identifying name for this Datos cluster:")
    Config.set('General', 'Datos-Cluster-Name',datos_name)
    datos_id = raw_input("Please provide identifying id (number) for this Datos cluster (This will be used for further communication w/ Datos):")
    Config.set('General', 'Datos-Cluster-Id',datos_id)
    box_id = raw_input("Please provide login (typically email address) for the user with privileges to the Datos Box folder:")
    Config.set('General', 'Box-User-Login',box_id)
    Config.write(cfgfile)
    cfgfile.close()
    print("Configuration File Generated Successfully")

def get_folder_id(client, folder_name, folder_id=0):
    # get the folder of the folder under folder with id = folder_id
    root_folder = client.folder(folder_id).get()
    try:
        items = root_folder.get_items(limit=100, offset=0)
    except BoxAPIException:
        print('get_items failed')
    for item in items:
        if (item.name == folder_name):
            return item.id

def upload_logs(client):

    # TODO
    # Handle case when the folder is empty or the customers folder is not present
    # Handle case with incomplete config file or if config file is not present
    
    config = ConfigParser.RawConfigParser()
    config.read('box.cfg')
    
    datos_customer_name = config.get('General', 'Customer-Name')
    datos_cluster_name = config.get('General', 'Datos-Cluster-Name')
    
    # Create a "SupportBundles_API" folder under root folder
    root_folder_id = 0 #default folder id for root folder
    support_bundle_folder_id = get_folder_id(client, "SupportBundles_API", root_folder_id)
    root_folder = client.folder(support_bundle_folder_id)
    try:
        root_folder.add_collaborator('shalabh.goyal@datos.io', CollaborationRole.EDITOR)
    except:
        pass
    if (support_bundle_folder_id is None):
        root_folder = client.folder(root_folder_id)
        support_bundle_folder = root_folder.create_subfolder("SupportBundles_API")
        support_bundle_folder_id = support_bundle_folder.id

    print ("Support bundle folder id = {0}".format(support_bundle_folder_id))
    # Create a "HomeDepot" folder under "SupportBundles_API" folder
    cust_folder_id = get_folder_id(client, datos_customer_name, support_bundle_folder_id)
    if (cust_folder_id is None):
        root_folder = client.folder(support_bundle_folder_id)
        cust_folder = root_folder.create_subfolder(datos_customer_name)
        cust_folder_id = cust_folder.id

    # Create a "Staging" folder under "HomeDepot" folder
    datos_cluster_folder_id = get_folder_id(client, datos_cluster_name,cust_folder_id)
    if (datos_cluster_folder_id is None):
        root_folder = client.folder(cust_folder_id)
        datos_cluster_folder = root_folder.create_subfolder(datos_cluster_name)
        datos_cluster_folder_id = datos_cluster_folder.id

    # Create a "Timestamp" folder under "Staging" folder
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d_%H') + "_Hrs"
    datos_timestamp_folder_id = get_folder_id(client, timestamp, datos_cluster_folder_id)
    if (datos_timestamp_folder_id is None):
        root_folder = client.folder(datos_cluster_folder_id)
        datos_timestamp_folder = root_folder.create_subfolder(timestamp)
        datos_timestamp_folder_id = datos_timestamp_folder.id

    testVar = raw_input("Please provide name of file to be uploaded:")
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), testVar)
    root_folder = client.folder(datos_timestamp_folder_id)
    a_file = root_folder.upload(file_path, file_name=testVar, upload_using_accelerator=True)
    try:
        print('{0} uploaded: '.format(a_file.get()['name']))
    except BoxAPIException:
        print('{0} upload failed: '.format(a_file.get()['name']))
        print("   " + item.name)
    print('{0} uploaded: '.format(testVar))


def main():

    args = handle_cli()

    if (args.setup):
        gen_config_file()
    elif (args.logs):
        upload_logs(get_auth())
    elif (args.callhome):
        send_callhome(get_auth())

    os._exit(0)
        

if __name__ == '__main__':
    main()

