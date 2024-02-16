import docker

class ClusterManager:
    def __init__(self):
        self.client = docker.from_env()

    def create_cluster(self, image_name="ubuntu:latest", num_containers=8):
        if not self.image_exists(image_name):
            print(f"Error: Image '{image_name}' not found.")
            return
        
        for i in range(num_containers):
            container = self.client.containers.run(image_name, detach=True)
        print(f"Cluster created with {num_containers} containers using image '{image_name}'.")

    def list_cluster(self):
        print("Current containers in the cluster:")
        for container in self.client.containers.list(all=True):
            print(container.short_id)

    def run_command_in_cluster(self, command):
        for container in self.client.containers.list():
            container.exec_run(command)
        print(f"Command '{command}' executed in all containers.")

    def stop_cluster(self):
        for container in self.client.containers.list():
            container.stop()
        print("Cluster stopped.")

    def delete_cluster(self):
        for container in self.client.containers.list(all=True):
            container.remove(force=True)
        print("Cluster containers deleted.")
    
    def image_exists(self, image_name):
        try:
            self.client.images.get(image_name)
            return True
        except docker.errors.ImageNotFound:
            return False

# Command line interface
def main():
    try:
        cm = ClusterManager()
    except:
        print("Cannot connect with docker server, please check if docker server is on.")
        return
    print("╔══════════════════════════════╗")
    print("║     Welcome to the Cluster   ║")
    print("║           Manager            ║")
    print("╚══════════════════════════════╝")
    print("  Type 'help' to see available   ")
    print("   commands or 'exit' to quit.    ")
    print("────────────────────────────────")
    print("                - Haohui Zheng   ")
    while True:
        user_input = input(">>> ").strip().split()
        command = user_input[0]

        if command == "exit":
            break
        elif command == "help":
            print("Available commands:")
            print("create [image_name] [num_containers]: Create a cluster with the specified number of containers (default is 8) using the specified image (default is ubuntu:latest)")
            print("list: List current containers in the cluster")
            print("run [command]: Run a command in all containers of the cluster")
            print("stop: Stop the cluster")
            print("delete: Delete the cluster")
            print("help: Display this help message")
            print("exit: Exit the program")
        elif command == "create":
            if len(user_input) == 1:
                image_name = "ubuntu:latest"
                num_containers = 8
            elif len(user_input) == 2:
                if user_input[1].isdigit():
                    image_name = "ubuntu:latest"
                    num_containers = int(user_input[1])
                else:
                    image_name = user_input[1]
                    num_containers = 8
            else:
                image_name = user_input[1]
                num_containers = int(user_input[2])
            cm.create_cluster(image_name, num_containers)
        elif command == "list":
            cm.list_cluster()
        elif command == "run":
            if len(user_input) < 2:
                print("Error: Please specify a command to run.")
            else:
                command_to_run = " ".join(user_input[1:])
                cm.run_command_in_cluster(command_to_run)
        elif command == "stop":
            cm.stop_cluster()
        elif command == "delete":
            cm.delete_cluster()
        else:
            print("Error: Unknown command. Type 'help' for available commands.")

if __name__ == "__main__":
    main()
