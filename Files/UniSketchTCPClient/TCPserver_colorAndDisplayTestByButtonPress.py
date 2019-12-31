#!/usr/bin/env python3
import socketserver
import socket
import base64
import time
import re

"""
	This test sends button colors and graphics as fast as possible
	Great burn-in test and flashing panel!

"""





class MyTCPHandler(socketserver.BaseRequestHandler):
	
	def handle(self):
		self.panelInitialized = False
		self.request.settimeout(0.5)	# How quick (in seconds) we will try to send new display and color data to the panel - moderated by looking for the BSY command though.
		dimmed = True	# Dim the panel colors
		color = 0

			# Text strings for display formatting
			# [value]:[format]:[fine]:[Title]:[isLabel]:[label 1 ]:[label 2]:[value2]:[values pair]:[scale]:[scale range low]:[scale range high]:[scale limit low]:[scale limit high]:[img]
		txtStrings = [
			'HWCt#{}=',	# Blank out display with empty string

				# Basic formatting
			'HWCt#{}=||||1|Basic|Formats|||||||||1|9|4',	# Header
			'HWCt#{}=12345|||No format',	# 32 bit integer
			'HWCt#{}=-1234567|||No format',	# 32 bit integer, negative
			'HWCt#{}=9999|7||Format=7',	# format 7 = empty!
			'HWCt#{}=99|2||Format=2',	# Integer value in Percent
			'HWCt#{}=12345|2||Format=2',	# Integer value in Percent
			'HWCt#{}=999|3||Format=3',	# Integer value in dB
			'HWCt#{}=12345|3||Format=3',	# Integer value in dB
			'HWCt#{}=1234|4||Format=4',	# Integer in frames
			'HWCt#{}=999|5||Format=5',	# Reciproc value of integer
			'HWCt#{}=9999|6||Format=6',		# Kelvin

				# Testing icons:
			'HWCt#{}=||||1|Test|Icons|||||||||1|9|4',	# Header
			'HWCt#{}=9999|2|1|Icon=1',	# "Fine" icon
			'HWCt#{}=9999|2|2|Icon=2',	# Lock icon
			'HWCt#{}=9999|2|3|Icon=3',	# No access
			'HWCt#{}=9999|2|8|C.Icon=1',	# Cycle
			'HWCt#{}=9999|2|16|C.Icon=2',	# Down
			'HWCt#{}=9999|2|24|C.Icon=3',	# Up
			'HWCt#{}=9999|2|32|C.Icon=4',	# Hold
			'HWCt#{}=9999|2|40|C.Icon=5',	# Toggle
			'HWCt#{}=9999|2|48|C.Icon=6',	# OK
			'HWCt#{}=9999|2|56|C.Icon=7',	# Question

				# Floating:
			'HWCt#{}=||||1|Floating|Point|||||||||1|9|4',	# Header
			'HWCt#{}=-50|1||Format=1',	# Float with 2 decimal points. Renders as -0.05
			'HWCt#{}=-550|1||Format=1',	# Float with 2 decimal points. Renders as -0.56
			'HWCt#{}=-5550|1||Format=1',	# Float with 2 decimal points.  Renders as -5.55
			'HWCt#{}=-55550|1||Format=1',	# Float with 2 decimal points.  Renders as -55.56
			'HWCt#{}=-5|8||Format=8',	# Float with 3 decimal points. Renders as -0.005
			'HWCt#{}=-55|8||Format=8',	# Float with 3 decimal points. Renders as -0.055
			'HWCt#{}=-555|8||Format=8',	# Float with 3 decimal points. Renders as -0.555
			'HWCt#{}=-5555|8||Format=8',	# Float with 3 decimal points. Renders as -5.555
			'HWCt#{}=-55555|8||Format=8',	# Float with 3 decimal points. Renders as -55.555
			'HWCt#{}=-5|9||Format=9',	# Float with 2 decimal points. Renders as -0.05
			'HWCt#{}=-55|9||Format=9',	# Float with 2 decimal points. Renders as -0.55
			'HWCt#{}=-555|9||Format=9',	# Float with 2 decimal points. Renders as -5.55
			'HWCt#{}=-5555|9||Format=9',	# Float with 2 decimal points. Renders as -55.55
			'HWCt#{}=-55555|9||Format=9',	# Float with 2 decimal points. Renders as -555.55
			'HWCt#{}=-5|12||Format=12',	# Float with 1 decimal points. Renders as -0.5
			'HWCt#{}=-55|12||Format=12',	# Float with 1 decimal points. Renders as -5.5
			'HWCt#{}=-555|12||Format=12',	# Float with 1 decimal points. Renders as -55.5
			'HWCt#{}=-5555|12||Format=12',	# Float with 1 decimal points. Renders as -555.5
			'HWCt#{}=-55555|12||Format=12',	# Float with 1 decimal points. Renders as -5555.5

				# Title Bar:
			'HWCt#{}=||||1|Title|Bar|||||||||1|9|4',	# Header
			'HWCt#{}=|||Bar = Value', # Title string as value (has a solid "bar" in title)
			'HWCt#{}=|||Line = Label|1',	# Title string as label (has a line under title string)
			'HWCt#{}=|||My Title|1|Font 1 8x8|As Label|||||||||8', # Title Font test
			'HWCt#{}=|||My Title||Font 1 8x8|As Value|||||||||8', # Title Font test
			'HWCt#{}=|||My Title|1|Font 2 5x5|As Label|||||||||16', # Title Font test
			'HWCt#{}=|||My Title||Font 2 5x5|As Value|||||||||16', # Title Font test
			'HWCt#{}=|||My Title||Font 1 8x8|Large|||||||||8|32', # Title Font Size test (wide font)
			'HWCt#{}=|||My Title||Font 1 8x8|Large|||||||||8|128', # Title Font Size test (tall font)
			'HWCt#{}=|||My Title||Font 1 8x8|Large|||||||||8|160', # Title Font Size test (double size font)

				# Text Labels
			'HWCt#{}=||||1|Text|Labels|||||||||1|9|4',	# Header
			'HWCt#{}=|||Short Text Label|1|Quick',	# Typical Text Label
			'HWCt#{}=|||Medium Text Label|1|Quick Dog',	# Typical Text Label
			'HWCt#{}=|||Long Text Label|1|Quick Dog Lazy Fox',	# Typical Text Label
			'HWCt#{}=|||Small Font|1|Quick Dog Lazy Fox|||||||||||5',	# Small text
			'HWCt#{}=|||Narrow Font|1|Quick Dog Lazy Fox|||||||||||9',	# Narrow text
			'HWCt#{}=|||One Label Line|1|Text1Label||0',	# Adding the zero (value 2) means we will print two lines and the text label will be in smaller printing
			'HWCt#{}=|||Two Label Lines|1|Text1Label|Text2Label',	# Printing two labels
			'HWCt#{}=|||Only Second Line|1||Text2Label',	# Printing only the second line
			'HWCt#{}=123|||Text & Value|1|Val1:|Val2:|456',	# First and second value is printed in small characters with prefix labels Val1 and Val2

				# Special text
			'HWCt#{}=||||1|Special|Text|||||||||1|9|4',	# Header
			'HWCt#{}=1|11||||The quick brown fox|jumps over the lazy dog.',	# Printing two labels, size 1
			'HWCt#{}=2|11||||The quick brown fox|jumps over the lazy dog.',	# Printing two labels, size 2
			'HWCt#{}=|11||||The quick brown fox|jumps over the lazy dog.||||||||||9',	# Printing two labels, size 1 tall
			'HWCt#{}=1|10||Quick brown fox jumps over the lazy dog.',	# Printing one label, size 1
			'HWCt#{}=2|10||Quick brown fox jumps over the lazy dog.',	# Printing one label, size 2
			'HWCt#{}=3|10||Quick brown fox jumps over the lazy dog.',	# Printing one label, size 3
			'HWCt#{}=4|10||Quick brown fox jumps over the lazy dog.',	# Printing one label, size 4
			'HWCt#{}=4|10||12345',	# Printing one label, size 4
			'HWCt#{}=|11||||The quick brown fox|Font 1|||||||||1',	# Another font
			'HWCt#{}=|11||||The quick brown fox|+Fixed Width|||||||||65',	# Another font, fixed width
			'HWCt#{}=|11||||The quick brown fox|Taller|||||||||1|9',	# Taller
			'HWCt#{}=|11||||The quick brown fox|+ char spacing|||||||||1|5|8',	# Extra character spacing

				# Pair of Coordinates
			'HWCt#{}=||||1|Pair of|Coordinates|||||||||1|9|4',	# Header
			'HWCt#{}=-1234|1||No Pair||x:|y:|4567|0',	# No box
			'HWCt#{}=-1234|1||No Box:||x:|y:|4567|1',	# Box type 1
			'HWCt#{}=-1234|1||Box Upper:||x:|y:|4567|2',	# Box type 2
			'HWCt#{}=-1234|1||Box Lower:||x:|y:|4567|3',	# Box type 3
			'HWCt#{}=-1234|1||Both Boxed:||x:|y:|4567|4',	# Box type 4

					# 1 = strength scale
			'HWCt#{}=||||1|Scale|Bar|||||||||1|9|4',	# Header
			'HWCt#{}=-2000|1||Scale 1||||||1|-2000|1000|-2000|1000',
			'HWCt#{}=-1000|1||Scale 1||||||1|-2000|1000|-2000|1000',
			'HWCt#{}=0|1||Scale 1||||||1|-2000|1000|-2000|1000',
			'HWCt#{}=10|1||Scale 1||||||1|-2000|1000|-2000|1000',
			'HWCt#{}=1000|1||Scale 1||||||1|-2000|1000|-2000|1000',
			'HWCt#{}=-550|1||Scale 1+L||||||1|-2000|1000|-1800|600',

					# 2 = centered marker scale
			'HWCt#{}=-2000|1||Scale 2||||||2|-2000|1000|-2000|1000',
			'HWCt#{}=-1000|1||Scale 2||||||2|-2000|1000|-2000|1000',
			'HWCt#{}=0|1||Scale 2||||||2|-2000|1000|-2000|1000',
			'HWCt#{}=10|1||Scale 2||||||2|-2000|1000|-2000|1000',
			'HWCt#{}=1000|1||Scale 2||||||2|-2000|1000|-2000|1000',
			'HWCt#{}=-550|1||Scale 2+L||||||2|-2000|1000|-1800|600',

					# 3 = centered bar
			'HWCt#{}=-2000|1||Scale 3||||||3|-2000|1000|-2000|1000',
			'HWCt#{}=-1000|1||Scale 3||||||3|-2000|1000|-2000|1000',
			'HWCt#{}=0|1||Scale 3||||||3|-2000|1000|-2000|1000',
			'HWCt#{}=10|1||Scale 3||||||3|-2000|1000|-2000|1000',
			'HWCt#{}=1000|1||Scale 3||||||3|-2000|1000|-2000|1000',
			'HWCt#{}=-500|1||Scale 3+L||||||3|-2000|1000|-1800|600',

			'HWCt#{}=-700|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-680|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-660|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-640|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-620|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-600|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-580|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-560|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-540|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-520|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-500|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-480|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-460|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-440|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-420|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-400|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-380|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-360|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-340|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-320|1||Scale 3+L||||||3|-2000|1000|-1800|600',
			'HWCt#{}=-300|1||Scale 3+L||||||3|-2000|1000|-1800|600',

			'HWCt#{}=||||||||||||||1',	# 1: First memory image

			'HWCt#{}=',	# Blank out display with empty string
			]

			# Images
		imageStrings = [
				[	# "D" in "DUMB"
					'HWCg#{}=0:///////gAAD///////+AAP////////AA/////////gD/////////gP/////////A//////////D///gAP///+P//+AAD///4///4AAD///z///gAAH8=',
					'HWCg#{}=1://7///gAAD///v//+AAAP//////4AAAf//////gAAB//////+AAAH//////4AAAf//////gAAB//////+AAAH//////4AAAf//////gAAD///v//+AA=',
					'HWCg#{}=2:AD///v//+AAAf//8///4AAH///z///gAD///+P/////////w/////////8D/////////gP////////4A////////8AD///////8AAP//////gAAA',
				],
				[	# TEST 64x48
					'HWCg#{}=0/4,64x48://///////////////////8hCEIQhCEITyEIQhCEIQhP//////////8hCEIQhCEITyEIQhCEIQhPIQhCEIQhCE8hCEIQhCEIT//////////8=',
					'HWCg#{}=1:yEIQhCEIQhPIQhCEIQhCE8hCEIQhCEITyEIQhCEIQhP//////////8hCEIQhCEITyEIQhCEIQhPIABCEIQACE8gAAAQgAAIT/H4DAHDh8f8=',
					'HWCg#{}=2:yP4HAADjuBPIwA8AAeMYE8jAHxzD4xgTyPwbD4bjuBP4/jMPhuHw/8jGdwcM47gTyMZ/hw/zGBPIxgcPgOMYE8juAx3A47gT/HwDGMDh8f8=',
					'HWCg#{}=3:yAAAAAAAAhPIABAAAQACE8hCEIQhCEITyEIQhCEIQhP//////////8hCEIQhCEITyEIQhCEIQhPIQhCEIQhCE8hCEIQhCEIT//////////8=',
					'HWCg#{}=4:yEIQhCEIQhPIQhCEIQhCE8hCEIQhCEITyEIQhCEIQhP//////////8hCEIQhCEIT/////////////////////w==',
				],
				[
					# TEST 96x48
					'HWCg#{}=0/7,96x48:////////////////////////////////xCEIQhCEIQhCEIQjxCEIQhCEIQhCEIQj////////////////xCEIQhCEIQhCEIQjxCEIQhCEIQg=',
					'HWCg#{}=1:QhCEI8QhCEIQhCEIQhCEI8QhCEIQhCEIQhCEI////////////////8QhCEIQhCEIQhCEI8QhCEIQhCEIQhCEI8QhCEIQhCEIQhCEI8QhCEI=',
					'HWCg#{}=2:EIQhCEIQhCP////////////////EIQhCEIQhCEIQhCPEIQhCEIQhCEIQhCPEIQgAAAQhAAIQhCPEIQgAAAQgAAIQhCP///x8HwBw4fH///8=',
					'HWCg#{}=3:xCEI7j8AAOO4EIQjxCEIxnAAAeMYEIQjxCEIxmAcw+MYEIQjxCEIxn4PhuO4EIQj///4/n8PhuHw////xCEIfmOHDOO4EIQjxCEIBmGHD/M=',
					'HWCg#{}=4:GBCEI8QhCAZzj4DjGBCEI8QhCP4/HcDjuBCEI////vwfGMDh8f///8QhCAAAAAAAAhCEI8QhCAAAAAEAAhCEI8QhCEIQhCEIQhCEI8QhCEI=',
					'HWCg#{}=5:EIQhCEIQhCP////////////////EIQhCEIQhCEIQhCPEIQhCEIQhCEIQhCPEIQhCEIQhCEIQhCPEIQhCEIQhCEIQhCP///////////////8=',
					'HWCg#{}=6:xCEIQhCEIQhCEIQjxCEIQhCEIQhCEIQjxCEIQhCEIQhCEIQjxCEIQhCEIQhCEIQj////////////////xCEIQhCEIQhCEIQj//////////8=',
					'HWCg#{}=7://///////////////////w==',
				],
				[
					# TEST 64x38
					'HWCg#{}=0/15,64x38://///////////////////8QhCA==',
					'HWCg#{}=1:QhCEIQvEIQhCEIQhC////////w==',
					'HWCg#{}=2:///EIQhCEIQhC8QhCEIQhCELxA==',
					'HWCg#{}=3:IQhCEIQhC8QhCEIQhCEL/////w==',
					'HWCg#{}=4://///8QhCEIQhCELxCEIQhCEIQ==',
					'HWCg#{}=5:C8QBCEIQAAELxAAAAgAAAQv8fg==',
					'HWCg#{}=6:AwAHwfH/xP4HAA/juQvAwA8AAA==',
					'HWCg#{}=7:YxgLwMAfHMBjGAvA/BsPgOO4Cw==',
					'HWCg#{}=8:+P4zD4fB8P/AxncHAGO4C8DGfw==',
					'HWCg#{}=9:hwBjGAvAxgcPgGMYC8TuAx3P4w==',
					'HWCg#{}=10:uQv8fAMYz8Hx/8QAAAAAAAELxA==',
					'HWCg#{}=11:AQgAAAABC8QhCEIQhCELxCEIQg==',
					'HWCg#{}=12:EIQhC///////////xCEIQhCEIQ==',
					'HWCg#{}=13:C8QhCEIQhCELxCEIQhCEIQvEIQ==',
					'HWCg#{}=14:CEIQhCEL///////////EIQhCEA==',
					'HWCg#{}=15:hCEL/////////////////////w==',
				],
				[
					# TEST 112x32
					'HWCg#{}=0/5,112x32://///////////////////////////////////8QhCEIQhCEIQhCEIQhDxCEIQhCEIQhCEIQhCEPEIQhCEIQhCEIQhCEIQ////////////w==',
					'HWCg#{}=1:///////EIQhCEIQhCEIQhCEIQ8QhCEIQhCEIQhCEIQhDxCEIQhCEIQhCEIQhCEPEIQhAEAQBCAAABCEIQ////+AAAAD+AAAf////xCEIQw==',
					'HWCg#{}=2:AcH4AH4fhCEIQ8QhCE8Hw/wAfx/EIQhDxCEITwfAHAADAcQhCEPEIQhDAcAczgMBxCEIQ////8MBwDj8BwOP////xCEIQwHA8Hg+DwQhCA==',
					'HWCg#{}=3:Q8QhCEMBwcA4Bw4EIQhDxCEIQwHBgHgDGAQhCEPEIQhDAcOAfAMYBCEIQ////9/H8/jOfx/f////xCEIT8fz+cZ+H8QhCEPEIQhAAAAAAA==',
					'HWCg#{}=4:AAAEIQhDxCEIQAAAAAAAAAQhCEPEIQhCEAQBCEIQhCEIQ///////////////////xCEIQhCEIQhCEIQhCEPEIQhCEIQhCEIQhCEIQ8QhCA==',
					'HWCg#{}=5:QhCEIQhCEIQhCEPEIQhCEIQhCEIQhCEIQ/////////////////////////////////////8=',
				],
				[
					# TEST 128x32
					'HWCg#{}=0/9,128x32:///////////////////////////////////////////EIQhCEIQhCEIQhCEIQhCHxCEIQhCEIQg=',
					'HWCg#{}=1:QhCEIQhCEIfEIQhCEIQhCEIQhCEIQhCH/////////////////////8QhCEIQhCEIQhCEIQhCEIc=',
					'HWCg#{}=2:xCEIQhCEIQhCEIQhCEIQh8QhCEIQhCEIQhCAIQhCEIfEIQhCEAAAAEIAACEIQhCH/////+AAAAA=',
					'HWCg#{}=3:/gAAH//////EIQhCAwfh+AB+H4EIQhCHxCEIQh8H8/wAfx/BCEIQh8QhCEIfAHOcAAMBwQhCEIc=',
					'HWCg#{}=4:xCEIQgMAc5zOAwHBCEIQh//////DAOH4/AcDj//////EIQhCAwPB+Hg+DwEIQhCHxCEIQgMDg5w=',
					'HWCg#{}=5:OAcOAQhCEIfEIQhCAwYDDHgDGAEIQhCHxCEIQgMGA5x8AxgBCEIQh//////fx/P8zn8f3/////8=',
					'HWCg#{}=6:xCEIQh/H8fnGfh/BCEIQh8QhCEIAAAAAAAAAIQhCEIfEIQhCEAAAAAAAACEIQhCHxCEIQhCEIQg=',
					'HWCg#{}=7:QgCEIQhCEIf/////////////////////xCEIQhCEIQhCEIQhCEIQh8QhCEIQhCEIQhCEIQhCEIc=',
					'HWCg#{}=8:xCEIQhCEIQhCEIQhCEIQh8QhCEIQhCEIQhCEIQhCEIf///////////////////////////////8=',
					'HWCg#{}=9://////////8=',
				],
				[
					# TEST 48x24
					'HWCg#{}=0/2,48x24:////////////////0IQhCEIT0IQhCEIT0IQhCEIT/AAf+A+f0AABAAADw4/AB+Bzw4zABvBzx5g=',
					'HWCg#{}=1:bmAw88+MxuBh89mPw8HjM9mNw4ODM//c44MH+//c58YH+8GPxufgM8GHjGfgM9AAAAAAA9AAAAA=',
					'HWCg#{}=2:AhPQhCEIQhP////////QhCEIQhP///////////////8=',
				],
				[
					# TEST 52x24
					'HWCg#{}=0/2,52x24:///////////////////EIQhCEIQ/xCEIQhCEP8QhCEIQhD/4AAf+A+f/wAAAQAAAP8fj4AH4HD8=',
					'HWCg#{}=1:xwJwAbwcP8YAM5gMPD/nAHG4GHx/x+Dg8HjMP8BhwODgzD/AYwDgwf4/wGMB8YH+P+fj8bn4DP8=',
					'HWCg#{}=2:x8PzGfgMP8AAAAAAAD/EAAAAAIQ/xCEIQhCEP//////////EIQhCEIQ///////////////////8=',
				],
				[
					# TEST 256x20
					'HWCg#{}=0/7,256x20://///////////////////////////////////////////////////////////////////////////////////////////////////wAAAAA=',
					'HWCg#{}=1:IQAAAIQhCEIQhCEIQhCEI4QhCEIQhCEIQhCEIwAAAAAhAAAAhCEIQhCEIQhCEIQjhCEIQhCEIQhCEIQjfwfg/gAP4PwEIQhCEIQhCEIQhCM=',
					'HWCg#{}=2:BCEIQhCEIQhCEIQjf4fh/gAP8f5///////////////9///////////////8DjgGAAABxzgQhCEIQhCEIQhCEIwQhCEIQhCEIQhCEIwOOA4A=',
					'HWCg#{}=3:cYBxhgQhCEIQhCEIQhCEIwQhCEIQhCEIQhCEIwcPg/g7gPGGBCEIQhCEIQhCEIQjBCEIQhCEIQhCEIQjDg/j/h8B4YYEIQhCEIQhCEIQhCM=',
					'HWCg#{}=4:BCEIQhCEIQhCEIQjPADzjh4DgYY///////////////8///////////////84AHOGDgcBhgQhCEIQhCEIQhCEIwQhCEIQhCEIQhCEI3AAc4Y=',
					'HWCg#{}=5:Hw4BhgQhCEIQhCEIQhCEIwQhCEIQhCEIQhCEI2AAcY4/jgHOBCEIQhCEIQhCEIQjBCEIQhCEIQhCEIQjf4/h/jOP8f4EIQhCEIQhCEIQhCM=',
					'HWCg#{}=6:BCEIQhCEIQhCEIQjf4/A/HHP8Pz///////////////////////////////8AAAAAAAAAAIQhCEIQhCEIQhCEI4QhCEIQhCEIQhCEIwAAAAA=',
					'HWCg#{}=7:AAAAAIQhCEIQhCEIQhCEI4QhCEIQhCEIQhCEI/////////////////////////////////////////////////////////////////////8=',
				],
				[
					# TEST 64x32
					'HWCg#{}=0/1,64x32://///////////////////8QhCEIQhCELxCEIQhCEIQvEIQhCEIQhC///////////xCEIQhCEIQvEIQhCEIQhC8QBCEIQBCELxAEIQhAAAAv8AOAP8AAAP8D8A4AB/D+LwfwHgAH8P4vDgA+AAA4Bi8OAD45wDgGL8/gbh2AcB5/D/DOH4fwPC8OOc4PA/B4Lw45/w8AOOAvDjn/HwA4wC/OOA4fgDnAfwfw=',
					'HWCg#{}=1:A45x/H+LwPgDnHH4f4vEAAAAAAAAC8QBCAAAAAAL//////8f8//EIQhCEIQhC8QhCEIQhCELxCEIQhCEIQvEIQhCEIQhC/////////////////////8=',
				],
				[
					# TEST 48x24
					'HWCg#{}=0/0,48x24:////////////////0IQhCEIT0IQhCEIT0IQhCEIT/AAf+A+f0AABAAADw4/AB+Bzw4zABvBzx5huYDDzz4zG4GHz2Y/DweMz2Y3Dg4Mz/9zjgwf7/9znxgf7wY/G5+AzwYeMZ+Az0AAAAAAD0AAAAAIT0IQhCEIT////////0IQhCEIT////////////////',
				],
			]


		rotationIndex = 0
		busy = False;
		lastMillis = 0

		#sendValue = 0;
		HWCtracker = [0] * 256
		HWCcolor = [2] * 256
		HWCdispContent = [0] * 256

		while True:
			try:
				# self.request is the TCP socket connected to the client
				self.data = self.request.recv(1024).strip()
			except socket.timeout:	
				pass
					# In case 
				if not busy:
					# self.request.settimeout(50)

					millis = int(round(time.time() * 1000))
					print(millis-lastMillis)
					lastMillis = millis
			else:
				if self.data != b'':
					for line in self.data.split(b"\n"):
						print("Client {} sent: '{}<NL>'".format(self.client_address[0], line.decode('ascii')))

						# just send back the same data, but upper-cased
						if line == b"list":
							self.request.sendall(b"\nActivePanel=1\nlist\n")
							self.panelInitialized = True
							busy = False
							print("- Returned state and assumes panel is now ready")

						if line == b"BSY":
							busy = True

						if line == b"RDY":
							busy = False

						if line == b"ping":
							self.request.sendall(b"ack\n")
							busy = False
							print("- Returned 'ack'")

						# Parse map= and turn on the button in dimmed mode for each. 
						# We could use the data from map to track which HWcs are active on the panel
						match = re.search(r"^map=([0-9]+):([0-9]+)$", line.decode('ascii'))
						if match:
							HWcServer = int(match.group(2));	# Extract the HWc number of the keypress from the match
							HWcClient = int(match.group(1));	# Extract the HWc number of the keypress from the match
							HWCtracker[HWcClient] = HWcServer;

						# Parse down trigger:
						match = re.search(r"^HWC#([0-9]+)(.([0-9]+))=Down$", line.decode('ascii'))
						if match:
							HWc = int(match.group(1));	# Extract the HWc number of the keypress from the match
							FourWayDirection = int(match.group(3));	# Extract the HWc number of the keypress from the match

							# Highlight the button and turn on binary output:
							outputline = "HWC#{}={}\n".format(HWc, 4 | 0x20)

							# Rotate color number:
							HWCcolor[HWc] = (HWCcolor[HWc] + 1)%17;	# Rotate the internally stored color number
							outputline = outputline + "HWCc#{}={}\n".format(HWc,HWCcolor[HWc] | 0x80)	# OR'ing 0x80 to identify the color as an externally imposed color. By default the least significant 6 bits will be an index to a color, but you can OR 0x40 and it will instead accept a rrggbb combination.
							self.request.sendall(outputline.encode('ascii'))
							print("- Returns: '{}'".format(outputline.replace("\n","<NL>")))

							if (FourWayDirection > 2):
								HWCdispContent[HWc] = (HWCdispContent[HWc] + 1)%(len(txtStrings)+len(imageStrings))
							else:
								HWCdispContent[HWc] = (HWCdispContent[HWc] + (len(txtStrings)+len(imageStrings)) - 1)%(len(txtStrings)+len(imageStrings))

							for a in range (0, 255):
								if HWCtracker[a] > 0 and (FourWayDirection == 2 or FourWayDirection == 8 or HWCtracker[a] == HWc):
									if (HWCdispContent[HWc] < len(txtStrings)):
										self.request.sendall(txtStrings[HWCdispContent[HWc]].format(HWCtracker[a]).encode('ascii')+b"\n")
									else:
										for b in range (0, len(imageStrings[HWCdispContent[HWc]-len(txtStrings)])):
											self.request.sendall(imageStrings[HWCdispContent[HWc]-len(txtStrings)][b].format(HWCtracker[a]).encode('ascii')+b"\n")

						# Parse Up trigger:
						match = re.search(r"^HWC#([0-9]+)(.([0-9]+))=Up$", line.decode('ascii'))
						if match:
							HWc = int(match.group(1));	# Extract the HWc number of the keypress from the match

							# Dim the button:
							outputline = "HWC#{}={}\n".format(HWc,5)
							self.request.sendall(outputline.encode('ascii'))
							print("- Returns: '{}'".format(outputline.replace("\n","<NL>")))

				else:
					print("{} closed".format(self.client_address[0]))
					break



class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass


HOST, PORT = "0.0.0.0", 9923

# Create the server, binding to localhost on port 9999
server = ThreadedTCPServer((HOST, PORT), MyTCPHandler, bind_and_activate=False)
server.allow_reuse_address = True
server.server_bind()
server.server_activate()

# Activate the server; this will keep running until you
# interrupt the program with Ctrl-C
server.serve_forever()

