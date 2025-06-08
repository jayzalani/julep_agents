from julep import Client
import time
import yaml
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.units import inch
import re

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

    with open('FoodieTourTask.yaml', 'r', encoding='utf-8') as file:
        task_definition = yaml.safe_load(file)
    
    # Create the task
    task = client.tasks.create(
        agent_id=agent_id,
        **task_definition
    )
    
    print(f"✅ Task created successfully! ID: {task.id}")
    return task

def create_custom_styles():
    """Create custom styles for the PDF document"""
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30,
        textColor=HexColor('#2E4057'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Subtitle style
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        spaceBefore=10,
        textColor=HexColor('#48639C'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # City header style
    city_header_style = ParagraphStyle(
        'CityHeader',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=15,
        spaceBefore=25,
        textColor=HexColor('#D4AF37'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        borderWidth=2,
        borderColor=HexColor('#D4AF37'),
        borderPadding=10
    )
    
    # Weather info style
    weather_style = ParagraphStyle(
        'WeatherInfo',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=15,
        spaceBefore=5,
        textColor=HexColor('#5A5A5A'),
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    
    # Meal header style
    meal_header_style = ParagraphStyle(
        'MealHeader',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=10,
        spaceBefore=20,
        textColor=HexColor('#C73E1D'),
        fontName='Helvetica-Bold'
    )
    
    # Restaurant highlight style
    restaurant_style = ParagraphStyle(
        'RestaurantHighlight',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        spaceBefore=8,
        textColor=HexColor('#2E4057'),
        fontName='Helvetica-Bold',
        backColor=HexColor('#F0F4F8'),
        borderWidth=1,
        borderColor=HexColor('#D4AF37'),
        borderPadding=8
    )
    
    # Body text style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        spaceBefore=4,
        textColor=black,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    # Dish highlight style
    dish_style = ParagraphStyle(
        'DishHighlight',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        spaceBefore=4,
        textColor=HexColor('#8B4513'),
        fontName='Helvetica-Bold'
    )
    
    return {
        'title': title_style,
        'subtitle': subtitle_style,
        'city_header': city_header_style,
        'weather': weather_style,
        'meal_header': meal_header_style,
        'restaurant': restaurant_style,
        'body': body_style,
        'dish': dish_style
    }

def parse_tour_content(raw_output):
    """Parse and structure the tour content"""
    try:
        # Clean and extract text content
        if isinstance(raw_output, str):
            content = raw_output
        elif isinstance(raw_output, dict):
            content = str(raw_output.get('complete_foodie_guide', raw_output))
        else:
            content = str(raw_output)
        

        content = re.sub(r'\*+', '', content)  # Remove asterisks
        content = re.sub(r'#+', '', content)   # Remove hash symbols
        content = re.sub(r'\n{3,}', '\n\n', content)  # Normalize line breaks        
        # Try to split by city patterns
        city_patterns = [
            r'(?:🌟\s*)?([A-Z][a-zA-Z\s]+)(?:\s*🌟)?',
            r'(?:City:|CITY:)\s*([A-Z][a-zA-Z\s]+)',
            r'([A-Z][A-Z\s]+)(?:\s*FOODIE TOUR)'
        ]
        
        # If we can't parse structured content, create a general format
        if not any(re.search(pattern, content) for pattern in city_patterns):
            return [{'city': 'Foodie Tour Guide', 'content': content, 'weather': 'Weather information included'}]
        
        # Simple parsing - split by major sections
        sections = re.split(r'(?:\n\s*){2,}(?=[A-Z][A-Z\s]+)', content)
        
        parsed_sections = []
        for section in sections:
            if len(section.strip()) > 50:  # Only include substantial content
                # Try to extract city name from the beginning
                city_match = re.search(r'^([A-Z][a-zA-Z\s]+)', section)
                city_name = city_match.group(1).strip() if city_match else "Featured City"
                
                parsed_sections.append({
                    'city': city_name,
                    'content': section.strip(),
                    'weather': 'Perfect weather for food exploration!'
                })
        
        return parsed_sections if parsed_sections else [{'city': 'Foodie Tour Guide', 'content': content, 'weather': 'Great weather for dining!'}]
        
    except Exception as e:
        print(f"⚠️ Content parsing warning: {e}")
        return [{'city': 'Foodie Tour Guide', 'content': str(raw_output), 'weather': 'Weather information available'}]

def create_pdf_report(content, cities, filename):
    """Create a professional PDF report"""
    try:
        # Create the PDF document
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Get custom styles
        styles = create_custom_styles()
        
        # Story list to hold all content
        story = []
        
        # Title page
        story.append(Paragraph("🍽️ ULTIMATE FOODIE TOUR GUIDE", styles['title']))
        story.append(Spacer(1, 20))
        story.append(Paragraph("Your Personalized Culinary Adventure", styles['subtitle']))
        story.append(Spacer(1, 30))
        
        # Generate metadata table
        metadata_data = [
            ["Generated On:", datetime.now().strftime("%B %d, %Y at %I:%M %p")],
            ["Cities Covered:", ", ".join(cities)],
            ["Tour Type:", "One-Day Culinary Experience"],
            ["Weather Considered:", "Yes - Indoor/Outdoor recommendations included"]
        ]
        
        metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#F0F4F8')),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#2E4057')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#D4AF37')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [HexColor('#FFFFFF'), HexColor('#F8F9FA')])
        ]))
        
        story.append(metadata_table)
        story.append(Spacer(1, 30))
        
        # Introduction
        intro_text = """
        Welcome to your expertly crafted foodie tour! This guide has been specially designed to take you on 
        a culinary journey through some of the world's most delicious destinations. Each tour considers the 
        local weather conditions to recommend the perfect dining experiences, from cozy indoor establishments 
        to delightful outdoor terraces.
        
        Our recommendations feature iconic local dishes paired with top-rated restaurants, ensuring you 
        experience the authentic flavors and culinary traditions of each destination. Whether you're seeking 
        a hearty breakfast, a leisurely lunch, or an elegant dinner, this guide will lead you to unforgettable 
        gastronomic adventures.
        """
        
        story.append(Paragraph("About This Guide", styles['meal_header']))
        story.append(Paragraph(intro_text, styles['body']))
        story.append(PageBreak())
        
        # Parse the content
        tour_sections = parse_tour_content(content)
        
        # Add each city section
        for i, section in enumerate(tour_sections):
            # City header
            story.append(Paragraph(f"🏙️ {section['city'].upper()}", styles['city_header']))
            story.append(Spacer(1, 15))
            
            # Weather information
            story.append(Paragraph(f"🌤️ Weather & Dining Conditions: {section['weather']}", styles['weather']))
            story.append(Spacer(1, 20))
            
            # Process the content to identify meals and restaurants
            content_text = section['content']
            
            # Split content into paragraphs and process
            paragraphs = content_text.split('\n')
            current_meal = None
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                
                # Check if this is a meal header
                if any(meal in paragraph.lower() for meal in ['breakfast', 'lunch', 'dinner', 'brunch']):
                    if 'breakfast' in paragraph.lower():
                        story.append(Paragraph("🌅 BREAKFAST EXPERIENCE", styles['meal_header']))
                        current_meal = 'breakfast'
                    elif 'lunch' in paragraph.lower():
                        story.append(Paragraph("☀️ LUNCH ADVENTURE", styles['meal_header']))
                        current_meal = 'lunch'
                    elif 'dinner' in paragraph.lower():
                        story.append(Paragraph("🌙 DINNER DELIGHT", styles['meal_header']))
                        current_meal = 'dinner'
                    elif 'brunch' in paragraph.lower():
                        story.append(Paragraph("🥞 BRUNCH BLISS", styles['meal_header']))
                        current_meal = 'brunch'
                    
                    story.append(Spacer(1, 10))
                
                # Check if this mentions a restaurant
                elif any(word in paragraph.lower() for word in ['restaurant', 'café', 'bistro', 'eatery', 'diner', 'bar']):
                    story.append(Paragraph(f"🏪 {paragraph}", styles['restaurant']))
                
                # Check if this mentions a dish
                elif any(word in paragraph.lower() for word in ['dish', 'cuisine', 'specialty', 'famous for', 'try the']):
                    story.append(Paragraph(f"🍽️ {paragraph}", styles['dish']))
                
                # Regular content
                else:
                    if len(paragraph) > 20:  # Only add substantial paragraphs
                        story.append(Paragraph(paragraph, styles['body']))
                
                story.append(Spacer(1, 8))
            
            # Add page break between cities (except for the last one)
            if i < len(tour_sections) - 1:
                story.append(PageBreak())
        
        # Footer page with tips
        story.append(PageBreak())
        story.append(Paragraph("🎯 FOODIE TOUR TIPS & RECOMMENDATIONS", styles['city_header']))
        story.append(Spacer(1, 20))
        
        tips = [
            "Make reservations in advance for popular restaurants, especially for dinner.",
            "Consider dietary restrictions and inform restaurants when booking.",
            "Try to arrive hungry - portions at recommended restaurants are often generous!",
            "Don't hesitate to ask servers for wine or beverage pairings with your meals.",
            "Take photos of your favorite dishes to remember your culinary journey.",
            "Keep an open mind and try dishes that are new to you - that's the spirit of food exploration!",
            "Consider the weather when choosing between indoor and outdoor seating options.",
            "Tip appropriately based on local customs and service quality."
        ]
        
        for tip in tips:
            story.append(Paragraph(f"• {tip}", styles['body']))
            story.append(Spacer(1, 6))
        
        story.append(Spacer(1, 30))
        story.append(Paragraph("Bon Appétit & Happy Eating! 🥂", styles['subtitle']))
        
        # Build the PDF
        doc.build(story)
        return True
        
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        print("💡 Make sure you have installed reportlab: pip install reportlab")
        return False

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
        
        # Step 5: Process and save results
        print("\n" + "=" * 60)
        if result.status == "succeeded":
            print("🎉 SUCCESS! Your foodie tours are ready!")
            print("=" * 60)
            
            # Create output directory
            output_dir = "foodie_tours_pdf"
            os.makedirs(output_dir, exist_ok=True)
            
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cities_str = "_".join([city.replace(" ", "").replace(",", "") for city in cities[:3]])
            filename = os.path.join(output_dir, f"foodie_tour_{cities_str}_{timestamp}.pdf")
            
            # Create PDF report
            print("📄 Creating professional PDF report...")
            pdf_success = create_pdf_report(result.output, cities, filename)
            
            if pdf_success:
                print(f"✅ Professional PDF report created successfully!")
                print(f"📂 Location: {os.path.abspath(filename)}")
                print(f"💡 Open this PDF file to view your complete foodie tour guide.")
                print(f"📖 The report includes weather considerations, restaurant recommendations, and detailed meal descriptions.")
            else:
                print("❌ Failed to create PDF. Please check the error messages above.")
            
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

def run_interactive_tour():
    """Run interactive tour generation"""
    try:
        # Create agent and task
        agent = create_foodie_tour_agent()
        task = load_and_create_task(agent.id)
        
        # Get custom cities
        custom_cities = interactive_mode()
        
        # Execute tour generation
        result = execute_foodie_tour(task.id, custom_cities)
        
        # Process results
        print("\n" + "=" * 60)
        if result.status == "succeeded":
            print("🎉 SUCCESS! Your custom foodie tours are ready!")
            print("=" * 60)
            
            # Create PDF
            output_dir = "foodie_tours_pdf"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cities_str = "_".join([city.replace(" ", "").replace(",", "") for city in custom_cities[:3]])
            filename = os.path.join(output_dir, f"custom_foodie_tour_{cities_str}_{timestamp}.pdf")
            
            print("📄 Creating your personalized PDF report...")
            pdf_success = create_pdf_report(result.output, custom_cities, filename)
            
            if pdf_success:
                print(f"✅ Custom PDF report created successfully!")
                print(f"📂 Location: {os.path.abspath(filename)}")
                
        else:
            print(f"❌ ERROR: {result.error}")
            
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    print("📋 First, make sure you have installed the required PDF library:")
    print("   pip install reportlab")
    print()
    
    # Choose mode
    print("Choose your mode:")
    print("1. Default cities (Mumbai, London, Paris, Tokyo, New York)")
    print("2. Choose your own cities")
    print("3. Quick test with single city")
    
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    
    if choice == "2":
        run_interactive_tour()
    elif choice == "3":
        # Quick test mode
        test_city = input("Enter a city name for quick test: ").strip() or "Mumbai"
        try:
            agent = create_foodie_tour_agent()
            task = load_and_create_task(agent.id)
            result = execute_foodie_tour(task.id, [test_city])
            
            if result.status == "succeeded":
                output_dir = "foodie_tours_pdf"
                os.makedirs(output_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(output_dir, f"test_tour_{test_city}_{timestamp}.pdf")
                
                pdf_success = create_pdf_report(result.output, [test_city], filename)
                if pdf_success:
                    print(f"✅ Quick test completed! Check: {os.path.abspath(filename)}")
            else:
                print(f"❌ Test failed: {result.error}")
                
        except Exception as e:
            print(f"❌ Test error: {str(e)}")
    else:
        # Default mode
        main()
    
    print("\n🙏 Thank you for using the Ultimate Foodie Tour Generator!")
    print("🍽️ Enjoy your culinary adventures!")