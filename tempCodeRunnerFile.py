
        try:
            # Parse the date and format it nicely
            date_obj = datetime.strptime(certificate_date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%B %d, %Y')
            
            # Add date to certificate
            date_font = ImageFont.truetype('MrDeHaviland-Regular.ttf', 35)
            date_position = (370, 900)  # Adjust position as needed
            draw.text(date_position, formatted_date, font=date_font, fill=(0, 0, 0))
        except ValueError:
            pass  # Skip if date format is invalid