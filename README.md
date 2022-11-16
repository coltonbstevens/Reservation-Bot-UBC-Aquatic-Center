# Reservation Bot - UBC Aquatic Center

https://user-images.githubusercontent.com/90413043/202296605-3c9b319d-d871-4926-8809-b729215f2765.mov

UBCReservations.py contains code to automatically reserve time slots at the UBC Aquatic Center using the Selenium Web Driver.

## Description

The most competitive time slots at fitness facilities often book up before you can even reserve them! 
Selenium's Web Driver speeds up the process, reserving your chosen time slot much faster than a human.

This project demonstrates how Seleniumn can be used to automatically reserve time slots.
The code is tailored to the UBC Aquatic center, but you can apply the same principles to almost any reservation system. 
The general steps are as follows:
- Load the URL with Selenium's WebDriver.
- Navigate input fields and buttons to progress through the reservation process (I used XPath to locate elements).
- Submit necessary information and reserve the chosen time slot.

You can tweak the script and use Cron or the Windows Task Manager to fully automate the reservation process.

## Author:

Colton Stevens




