

import requests
import json
import os
import sys
DOWNLOAD_PATH = ".downloads/"

def download_pack_index_file(pack_type):
    dev_file_url = "https://espressif.github.io/arduino-esp32/package_esp32_dev_index.json"
    stable_file_url = "https://espressif.github.io/arduino-esp32/package_esp32_index.json"

    if pack_type == "dev":
        file_url = dev_file_url
    elif pack_type == "stable":
        file_url = stable_file_url
    else:
        print("Invalid pack type!")
        return False

    try:
        if not os.path.exists(DOWNLOAD_PATH):
            os.makedirs(DOWNLOAD_PATH)

        response = requests.get(file_url)
        if response.status_code == 200:
            file_name = os.path.basename(file_url)
            file_path = os.path.join(DOWNLOAD_PATH, file_name)
            with open(file_path, "w") as f:
                f.write(response.text)
            print(f"Download package index file '{file_name}' successfully!")
            return file_name
        else:
            print("Failed to download package index file!")
            return False
    except requests.exceptions.RequestException as e:
        print("Error: ", e)
        return False


# 定义一个递归函数来查找所有的 version
def find_json_handle(obj, handle):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == handle:

                print("find handle: "+value)  # 打印找到的 version

                return value
            # 递归查找
            find_json_handle(value)
    elif isinstance(obj, list):
        for item in obj:
            find_json_handle(item)


def download_file(url, pack_size, dest_folder):
    # 下载文件
    
    try:
        if not os.path.isdir(dest_folder):
            os.makedirs(dest_folder)  # 创建目标文件夹
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        file_name = os.path.join(dest_folder, url.split('/')[-1])  # 获取文件名
        with open(file_name, 'wb') as f:
            f.write(response.content)  # 将内容写入文件
        print(f"Downloaded: {file_name}")

        actual_size = os.path.getsize(file_name)  # 获取文件大小
        if actual_size != pack_size:
            print(f"Warning: {file_name} size is {actual_size} bytes, expected {pack_size} bytes.")
            return None  # 返回 None 表示下载失败
        else:
            print(f"Downloaded {file_name} successfully!")
            return file_name  # 返回下载的文件名
    except Exception as e:
        print(f"Failed to download {url}. Reason: {str(e)}")
        return None  # 返回 None 表示下载失败

# 查找需要的信息
def parse_pack_index_file(file_name, find_version, pc_arch):
    # 读取 JSON 文件
    with open(DOWNLOAD_PATH+file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)

        # 使用一个列表来存储Tools的名字和版本
        tools_list = []
        tools_download_url_list = []

        # 遍历 package 和 platforms，提取相关信息
        for package in data.get('packages', []):
            platforms = package.get('platforms', [])
            for platform in platforms:
                if platform.get('name') == 'esp32':
                    version = platform.get('version')
                    url = platform.get('url')
                    archive_file_name = platform.get('archiveFileName')
                    # print(f"Version: {version}")
                    # print(f"URL: {url}")
                    # print(f"Archive File Name: {archive_file_name}")
                    # print('-' * 40)

                    if find_version == version:
                        print(f"Version: {version}")
                        print(f"URL: {url}")
                        print(f"Archive File Name: {archive_file_name}")
                        print('-' * 40)

                        #下载对应package

                        # 遍历工具依赖
                        tools_dependencies = platform.get('toolsDependencies', [])
                        tool_index = 1
                        for tool in tools_dependencies:
                            tool_name = tool.get('name')
                            tool_version = tool.get('version')
                            tools_list.append((tool_name, tool_version))

                            print(f"[{tool_index}]Tool: {tool_name}: {tool_version}")
                            tool_index += 1
                            # print(f"Tool Version: ")
                        print('-' * 40)


                        # # 打印所有工具的名字和版本
                        # print("Tools and their versions:")
                        # for name, name in tools_list:
                        #     print(f"Tool: {name}, Version: {version}")
                        # print('-' * 40)


                        # 找到下载链接
                        tool_index = 1
                        for tool_name, tool_version in tools_list:
                            for package in data.get('packages', []):
                                tools = package.get('tools', [])
                                # print(tools)
                                for tool in tools:
                                   if tool.get('name') == tool_name and tool.get('version') == tool_version:
                                        systems = tool.get('systems', [])
                                        for system in systems:
                                            # print(f"Tool: {tool_name}, Version: {tool_version}, Host: {system['host']}")

                                            if system['host'] == pc_arch:
                                                # print(f"Host: {system['host']}")
                                                pack_url = system['url']
                                                pack_size = system['size']
                                                print(f"[{tool_index}]Download URL: {system['url']}")

                                                # tools_download_url_list.append((tool_name, pack_url, pack_size))
                                                tools_download_url_list.append((tool_name, pack_url, pack_size))  # 存储工具信息
                                                tool_index += 1
                                                # print(f"Archive File Name: {system['archiveFileName']}")
                                                # print(f"Checksum: {system['checksum']}")
                                                # print(f"Size: {system['size']}")
                        print('-' * 40)
    return tools_download_url_list


if __name__ == '__main__':
    print("Hello, world!")
    # 下载最新稳定版的包索引文件
    # down_ret = download_pack_index_file('dev')
    # down_file = download_pack_index_file('stable')
    # if down_file == False:
    #     print("Failed to download package index file!")
    #     sys.exit(1)

    down_file = "package_esp32_index.json"
    # 解析包索引文件
    download_links = parse_pack_index_file(down_file, "3.0.7",  'i686-mingw32')
     # 下载 tools_download_url_list 中的各个下载链接
    for tool_name, pack_url, pack_size in download_links:
        down_ret = download_file(pack_url, pack_size, DOWNLOAD_PATH)
        if down_ret == None:    #失败停止下载
            break
