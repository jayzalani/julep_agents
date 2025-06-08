from julep import Client
import time
import yaml

# Initialize the client with your API key
client = Client(api_key="eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0YmRkYjdhNi0wNTBkLTU5NjUtOTE2YS0yNDRhZjMwMWI5NzAiLCJlbWFpbCI6ImZyZXNoOTQwNUBnbWFpbC5jb20iLCJpYXQiOjE3NDkzNDkyNDgsImV4cCI6MTc0OTk1NDA0OH0.XXAAQlkIJPyhgo6jj-xXXm1883qLUiB7vFGBJt85e0PJAs8LGsavjX6rnOdW2z3ejinHuxkkoXeGAla63p2qfw")

def create_foodie_tour_agent():
    """Create the foodie tour agent"""
    print("🍽️ Creating Foodie Tour Agent...")
    
    agent = client.agents.create(
        name="Julep Foodie Tour Agent",
        about="A specialized culinary expert that creates immersive one-day foodie tours, "
              "considering weather conditions and featuring iconic local dishes with top-rated restaurants. "
              "Crafts delightful breakfast, lunch, and dinner narratives for the ultimate culinary experience.",
    )
    
    print(f"✅ Agent created successfully! ID: {agent.id}")
    return agent

def load_and_create_task(agent_id):
    """Load the task definition and create the task"""
    print("📋 Loading task configuration...")
    
    # Load the task definition from YAML file with UTF-8 encoding
    with open('FoodieTourTask.yaml', 'r', encoding='utf-8') as file:
        task_definition = yaml.safe_load(file)
    
    # Create the task
    task = client.tasks.create(
        agent_id=agent_id,
        **task_definition
    )
    
    print(f"✅ Task created successfully! ID: {task.id}")
    return task

def execute_foodie_tour(task_id, cities):
    """Execute the foodie tour for the given cities"""
    print(f"🚀 Starting foodie tour generation for cities: {', '.join(cities)}")
    
    # Create the execution
    execution = client.executions.create(
        task_id=task_id,
        input={
            "cities": cities
        }
    )
    
    print(f"⏳ Execution started. ID: {execution.id}")
    print("Processing... This may take a few minutes as we gather weather data, research local dishes, and find top restaurants.")
    
    # Monitor execution progress
    step_count = 0
    while (result := client.executions.get(execution.id)).status not in ['succeeded', 'failed']:
        current_status = result.status
        if step_count % 10 == 0:  # Print status every 10 iterations to avoid spam
            print(f"📊 Status: {current_status}")
        step_count += 1
        time.sleep(2)  # Check every 2 seconds
    
    return result

def main():
    """Main function to orchestrate the foodie tour creation"""
    print("🌟 Welcome to the Ultimate Foodie Tour Generator! 🌟")
    print("=" * 60)
    
    try:
        # Step 1: Create the agent
        agent = create_foodie_tour_agent()
        
        # Step 2: Load and create the task
        task = load_and_create_task(agent.id)
        
        # Step 3: Define cities for foodie tours
        cities = ["Mumbai", "London", "Paris", "Tokyo", "New York"]
        
        # Step 4: Execute the foodie tour generation
        result = execute_foodie_tour(task.id, cities)
        
        # Step 5: Display results
        print("\n" + "=" * 60)
        if result.status == "succeeded":
            print("🎉 SUCCESS! Your foodie tours are ready!")
            print("=" * 60)
            print(result.output)
        else:
            print(f"❌ ERROR: {result.error}")
            print("Please check your API keys and try again.")
            
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        print("Please check your configuration and try again.")

def interactive_mode():
    """Interactive mode for custom city selection"""
    print("\n🎯 Interactive Mode - Choose Your Own Cities!")
    print("=" * 50)
    
    cities = []
    while True:
        city = input("Enter a city name (or 'done' to finish): ").strip()
        if city.lower() == 'done':
            break
        if city:
            cities.append(city)
            print(f"✅ Added: {city}")
    
    if not cities:
        print("❌ No cities selected. Using default cities.")
        return ["Mumbai", "London", "Paris", "Tokyo", "New York"]
    
    return cities

if __name__ == "__main__":
    # Option 1: Run with default cities
    print("Choose your mode:")
    print("1. Default cities (Mumbai, London, Paris, Tokyo, New York)")
    print("2. Choose your own cities")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "2":
        # Interactive mode
        agent = create_foodie_tour_agent()
        task = load_and_create_task(agent.id)
        custom_cities = interactive_mode()
        result = execute_foodie_tour(task.id, custom_cities)
        
        print("\n" + "=" * 60)
        if result.status == "succeeded":
            print("🎉 SUCCESS! Your custom foodie tours are ready!")
            print("=" * 60)
            print(result.output)
        else:
            print(f"❌ ERROR: {result.error}")
    else:
        # Default mode
        main()