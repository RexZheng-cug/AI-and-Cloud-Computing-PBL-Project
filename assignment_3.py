import docker
import numpy as np
import os

class ClusterManager:
    def __init__(self):
        self.client = docker.from_env()

    def create_cluster(self, image_name="ubuntu:latest", num_containers=8):
        if not self.image_exists(image_name):
            print(f"Error: Image '{image_name}' not found.")
            return
        
        for i in range(num_containers):
            container = self.client.containers.run(image_name, detach=True, tty=True, stdin_open=True)
        print(f"Cluster created with {num_containers} containers using image '{image_name}'.")

    def list_cluster(self):
        print("Current containers in the cluster:")
        for container in self.client.containers.list(all=True):
            print(container.short_id)

    def run_command_in_cluster(self, command):
        for container in self.client.containers.list(all=True):
            if container.status != "running":
                container.start()
            exec_result = container.exec_run(command)
            print(f"Output for container {container.short_id}:")
            print(exec_result.output.decode())
        print(f"Command '{command}' executed in all containers.")
   
    def stop_cluster(self):
        for container in self.client.containers.list():
            container.stop()
        print("Cluster stopped.")

    def delete_cluster(self):
        for container in self.client.containers.list(all=True):
            container.remove(force=True)
        print("Cluster containers deleted.")
    
    def create_data_volume(self):
        self.client.volumes.create(name="data_volume", driver="local")
        print("Data volume created.")
        
    def generate_random_data(self, data_size=100000):
        file_path = "data.txt"
        volume_name = "data_volume"
        volume_path = f"/{volume_name}/{file_path}"  

        # Generate random data
        data = np.random.randint(0, 100, size=data_size)

        # Save data to local file
        with open(file_path, 'w') as file:
            np.savetxt(file, data)

        try:
            # Get volume path
            volume_info = self.client.volumes.get(volume_name)
            container_volume_path = volume_info.attrs['Mountpoint']

            # Copy local file to container
            container_file_path = os.path.join(container_volume_path, file_path)
            with open(file_path, 'rb') as local_file:
                container = self.client.containers.create("ubuntu:latest", command=f"python /app/linear_regression.py {file_path}", volumes={volume_name: {'bind': '/data', 'mode': 'rw'}})
                container.start()
                container.exec_run(f"mkdir -p /data")
                container.put_archive('/data', local_file.read())

            print("Random data generated and copied to data volume.")
        finally:
            # Delete local file
            os.remove(file_path)
    
    def distribute_data_to_containers(self):
        for container in self.client.containers.list():
            container_id = container.id[:12]
            command = f"cp /data/data.txt /app/data{container_id}.txt"
            container.exec_run(command)
        print("Data distributed to containers.")
        
    def run_processing_in_containers(self):
        data_size = 100000  
        data_per_container = data_size // len(self.client.containers.list())
        results = {}

        for idx, container in enumerate(self.client.containers.list()):
            start_index = idx * data_per_container
            end_index = (idx + 1) * data_per_container if idx != len(self.client.containers.list()) - 1 else data_size
            command = f"python process_data.py {start_index} {end_index}"
            exec_result = container.exec_run(command)
            result = exec_result.output.decode().strip().split('\n')
            results[container.short_id] = {
                'sum': float(result[0]),
                'average': float(result[1]),
                'max': float(result[2]),
                'min': float(result[3]),
                'standard_deviation': float(result[4])
            }

        print("Processing completed in containers. Results:")
        for container_id, result in results.items():
            print(f"Container {container_id}:")
            print(f"Sum: {result['sum']}")
            print(f"Average: {result['average']}")
            print(f"Max: {result['max']}")
            print(f"Min: {result['min']}")
            print(f"Standard Deviation: {result['standard_deviation']}")

    
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
            print("create: Create a cluster")
            print("list: List current containers in the cluster")
            print("run: Run a command in all containers of the cluster")
            print("stop: Stop the cluster")
            print("delete: Delete the cluster")
            print("volume: Create a data volume")
            print("generate: Generate random data and copy it to the data volume")
            print("distribute: Distribute data to containers")
            print("process: Run data processing in containers")
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
        elif command == "volume":
            cm.create_data_volume()
        elif command == "generate":
            data_size = int(user_input[1]) if len(user_input) > 1 else 100000
            cm.generate_random_data(data_size)
        elif command == "distribute":
            cm.distribute_data_to_containers()
        elif command == "process":
            cm.run_processing_in_containers()
        else:
            print("Error: Unknown command. Type 'help' for available commands.")

if __name__ == "__main__":
    main()

