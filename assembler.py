import re


# Instruction template
class instruction:
	def __init__(self):
		self.op_code = ""
		self.literal_symbol_address = 0
		self.physical_address = 0
		self.error = ""


# Symbol template
class symbol:
	def __init__(self, symbol_value):
		self.symbol_value = symbol_value
		self.symbol_address = 0


# Literal template
class literal:
	def __init__(self, literal_value):
		self.literal_value = literal_value
		self.literal_address = 0


# Assembler template
class assembler:
	def __init__(self):
		self.instruction_types = []
		self.final_literal_table = []
		self.final_symbol_table = []
		self.final_instruction_table = []
		self.final_variable_table = []
		# By default location counter & base_register get initialized with 100 if program doesn't start with 'START'
		self.location_counter = 100
		self.base_register = 14000
		self.op_codes = {"LAC": "0001",
		                 "SAC": "0010",
		                 "ADD": "0011",
		                 "SUB": "0100",
		                 "MUL": "1010",
		                 "DIV": "1011",
		                 "INP": "1000",
		                 "DSP": "1001",
		                 "BRZ": "0101",
		                 "BRN": "0110",
		                 "BRP": "0111",
		                 "CLA": "0000",
		                 "STP": "1100"
		                 }

	@staticmethod
	def isLiteral(s):
		try:
			int(s)
			return True
		except ValueError:
			return False

	def isSymbol(self, line):
		try:
			startsWithL = line.index('L')
		except ValueError:
			startsWithL = -1
		if startsWithL == 0 and self.isLiteral(line[1:]):
			return True

		return False

	def isRealSymbol(self, line):
		try:
			startsWithL = line.index('L')
		except ValueError:
			startsWithL = -1
		if (startsWithL == 0 and self.isLiteral(line[1:-1])) and line[-1] == ':':
			return True

		return False

	@staticmethod
	def isVariable(s):
		try:
			int(s)
			return False
		except ValueError:
			return True

	""" checkInstruction() checks if a particular line is a valid instruction.
		By default line is matched with all instruction types.
		To check if an instruction has a literal operand pass start = 0 & end = 8.
		To check if an instruction has a symbol operand pass start = 8 & end = 11.
		To check if an instruction is not having any operand pass start = 11.
	"""
	def checkInstruction(self, line, start=0, end=13):
		flag = 0
		for i in range(start, end):
			if bool(re.match(self.instruction_types[i], line)):
				flag = 1
				break

		if flag == 1:
			return True

		return False

	"""getSymbol() returns the symbol stripping of ':' character if present"""
	@staticmethod
	def getSymbol(line):
		if line[-1] == ':':
			return line[0:-1]
		else:
			return line

	"""getLiteral() typecasts given line to integer type"""
	@staticmethod
	def getLiteral(line):
		return int(line)

	"""removeDuplicateSymbol() removes duplicates of any symbol if present in symbol table"""
	def removeDuplicateSymbol(self, symbolTable):
		dummySymbolTable = []
		for i in range(len(symbolTable)):
			if symbolTable[i].symbol_address != 0:
				dummySymbolTable.append(symbolTable[i])
		for i in range(len(symbolTable)):
			flag = 0
			for j in range(len(dummySymbolTable)):
				if bool(re.match(dummySymbolTable[j].symbol_value, symbolTable[i].symbol_value)):
					flag = 1
					break
			if flag == 0:
				dummySymbolTable.append(symbolTable[i])
				print(symbolTable[i].symbol_value + "Symbol not defined!")
		for i in range(len(dummySymbolTable)):
			flag = 0
			for j in range(len(self.final_symbol_table)):
				if bool(re.match(self.final_symbol_table[j].symbol_value, dummySymbolTable[i].symbol_value)):
					flag += 1
			if flag == 0:
				self.final_symbol_table.append(dummySymbolTable[i])
			else:
				print(dummySymbolTable[i].symbol_value + "Symbol is defined again!")
		return self.final_symbol_table

	"""removeDuplicateVariable() removes duplicates of any symbol/variable if present in variable table"""
	@staticmethod
	def removeDuplicateVariable(variableTable):
		realVariables = []
		for i in range(len(variableTable)):
			flag = 0
			for j in range(len(realVariables)):
				if bool(re.match(realVariables[j].symbol_value, variableTable[i].symbol_value)):
					flag = 1
					break
			if flag == 0:
				realVariables.append(variableTable[i])

		return realVariables

	@staticmethod
	def removeDuplicateLiteral(literalTable):
		realLiterals = []
		for i in range(len(literalTable)):
			flag = 0
			for j in range(len(realLiterals)):
				if bool(re.match(realLiterals[j].literal_value, literalTable[i].literal_value)):
					flag = 1
					break
			if flag == 0:
				realLiterals.append(literalTable[i])

		return realLiterals

	def secondPass(self, instructionArray):
		for i in range(len(instructionArray)):
			firstIns = instructionArray[i][0]
			try:
				escapeIndex = firstIns.index("//")
			except ValueError:
				escapeIndex = -1
			if escapeIndex == -1:
				if bool(re.match("START", firstIns)) is False and bool(re.match("END", firstIns)) is False:
					new_instruction = instruction()
					for j in range(len(instructionArray[i])):
						if self.isRealSymbol(instructionArray[i][0]) is False and self.checkInstruction(instructionArray[i][0]) is False:
							new_instruction.error = "Sorry! not a legal opcode."
							break
						elif self.isRealSymbol(instructionArray[i][0]) and self.checkInstruction(instructionArray[i][1]) is False:
							new_instruction.error = "Sorry! not a legal opcode."
							break
						elif self.checkInstruction(instructionArray[i][j]):
							op_code = self.op_codes[instructionArray[i][j]]
							new_instruction.op_code = op_code

							# check if instruction contains literal
							if self.checkInstruction(instructionArray[i][j], 0, 8):
								if len(instructionArray[i]) > (j + 2):
									new_instruction.error = "Only one literal operand should be present"
								elif len(instructionArray[i]) < (j + 2):
									new_instruction.error = "An operand should be present"
								else:
									if self.isLiteral(instructionArray[i][j + 1]):
										for k in range(len(self.final_literal_table)):
											if self.getLiteral(instructionArray[i][j + 1]) == self.final_literal_table[
												k].literal_value:
												new_instruction.literal_symbol_address = self.final_literal_table[
													k].literal_address
												new_instruction.physical_address = self.base_register + new_instruction.literal_symbol_address
									elif self.isVariable(instructionArray[i][j + 1]):
										for k in range(len(self.final_symbol_table) - 1, -1, -1):
											if bool(re.match(self.final_symbol_table[k].symbol_value,
											                 instructionArray[i][j + 1])):
												new_instruction.literal_symbol_address = self.final_symbol_table[
													k].symbol_address
												new_instruction.physical_address = self.base_register + new_instruction.literal_symbol_address
												break
									else:
										new_instruction.error = "The operand should either be a literal or a variable"

							# check if instruction contains symbol
							if self.checkInstruction(instructionArray[i][j], 8, 11):
								if len(instructionArray[i]) > (j + 2):
									new_instruction.error = "Only one symbol operand should be present"
								elif len(instructionArray[i]) < (j + 2):
									new_instruction.error = "An operand should be present"
								else:
									if self.isSymbol(instructionArray[i][j + 1]):
										for k in range(len(self.final_symbol_table)):
											if bool(re.match(self.final_symbol_table[k].symbol_value,
											                 self.getSymbol(instructionArray[i][j + 1]))):
												new_instruction.literal_symbol_address = self.final_symbol_table[
													k].symbol_address
												new_instruction.physical_address = self.base_register + new_instruction.literal_symbol_address
									else:
										new_instruction.error = "Operand should be a symbol"

							# check if instruction contains no operand
							if self.checkInstruction(instructionArray[i][j], 11):
								if len(instructionArray[i]) > j + 1:
									new_instruction.error = "No operand should be present"

					self.final_instruction_table.append(new_instruction)

	def firstPass(self, instructionArray, literalTable, symbolTable, variableTable):
		for i in range(len(instructionArray)):
			firstIns = instructionArray[i][0]
			try:
				escapeIndex = firstIns.index("//")
			except ValueError:
				escapeIndex = -1

			if escapeIndex == -1:
				if bool(re.match("START", firstIns)) is False and bool(re.match("END", firstIns)) is False:
					keywordsLen = len(instructionArray[i])
					for j in range(keywordsLen):
						line = instructionArray[i][j]
						if self.isLiteral(line):
							lit = literal(self.getLiteral(line))
							literalTable.append(lit)

						if self.isSymbol(line):
							sym = symbol(self.getSymbol(line))
							symbolTable.append(sym)

						if self.isRealSymbol(line):
							sym = symbol(self.getSymbol(line))
							sym.symbol_address = self.location_counter
							symbolTable.append(sym)
							self.location_counter += 1

						if self.checkInstruction(line):
							self.location_counter += 1
							# check if instruction contains literal
							if self.checkInstruction(line, 0, 8):
								if (j + 1) < keywordsLen and self.isVariable(instructionArray[i][j + 1]):
									sym = symbol(instructionArray[i][j + 1])
									variableTable.append(sym)

		if len(literalTable) > 0:
			self.final_literal_table = self.removeDuplicateLiteral(literalTable)
			for i in range(len(self.final_literal_table)):
				self.final_literal_table[i].literal_address = self.location_counter
				self.location_counter += 1

		if len(symbolTable) > 0:
			self.final_symbol_table = self.removeDuplicateSymbol(symbolTable)

		if len(variableTable) > 0:
			self.final_variable_table = self.removeDuplicateVariable(variableTable)
			for i in range(len(self.final_variable_table)):
				self.final_variable_table[i].symbol_address = self.location_counter
				self.location_counter += 1
				self.final_symbol_table.append(self.final_variable_table[i])

		self.secondPass(instructionArray)

	def main(self):
		literal_list = []
		symbol_list = []
		instruction_list = []
		variable_list = []
		# setInstructions
		self.instruction_types = list(self.op_codes.keys())
		# open instructions file
		code_file = open("codes.txt", "r")
		# Read code_file and append all instructions into a list.
		for line_ins in code_file:
			line_ins = line_ins.strip()
			instruction_list.append(line_ins.split(' '))

		code_file.close()

		if bool(re.match('START', instruction_list[0][0])):
			if len(instruction_list[0]) == 2 and self.isLiteral(instruction_list[0][1]):
				self.location_counter = self.getLiteral(instruction_list[0][1])
			else:
				print("No Literal present beside 'START'")
		else:
			print("Location counter is by default set to 100 since program not starting with 'START'")

		self.firstPass(instruction_list, literal_list, symbol_list, variable_list)

		# Create/Overwrite the outputCodes txt file
		output_file = open('outputCodes.txt', 'w')

		# output literal table
		print("LITERAL TABLE: ")
		output_file.write("LITERAL TABLE: \n")
		output_file.write('--------------------------------- \n')
		output_file.write('| LITERAL_VALUE | LITERAL_ADDRESS | \n')
		output_file.write('---------------------------------- \n')
		for i in range(len(self.final_literal_table)):
			print(self.final_literal_table[i].literal_value, self.final_literal_table[i].literal_address)
			output_file.write(' \t' + str(self.final_literal_table[i].literal_value))
			output_file.write(' \t\t\t\t' + str(self.final_literal_table[i].literal_address) + '\n')
		print('', end='\n')
		output_file.write('---------------------------------- \n\n')

		# output symbol table
		print("SYMBOL TABLE:")
		output_file.write("SYMBOL TABLE: \n")
		output_file.write('--------------------------------- \n')
		output_file.write('| SYMBOL_VALUE | SYMBOL_ADDRESS | \n')
		output_file.write('--------------------------------- \n')
		for i in range(len(self.final_symbol_table)):
			print(self.final_symbol_table[i].symbol_value, self.final_symbol_table[i].symbol_address)
			output_file.write(' \t' + str(self.final_symbol_table[i].symbol_value))
			output_file.write(' \t\t\t\t' + str(self.final_symbol_table[i].symbol_address) + '\n')
		print('', end='\n')
		output_file.write('--------------------------------- \n\n')

		# output instruction table
		print("INSTRUCTION TABLE:")
		output_file.write('INSTRUCTION TABLE: \n')
		output_file.write('----------------------------------------------- \n')
		output_file.write('| OP_CODE | SYMBOL_ADDRESS | PHYSICAL_ADDRESS | \n')
		output_file.write('----------------------------------------------- \n')
		for i in range(len(self.final_instruction_table)):
			ithInstruction = self.final_instruction_table[i]
			print(ithInstruction.op_code, end=' ')
			output_file.write('\t' + ithInstruction.op_code + '\t\t')
			symbolAddress = ithInstruction.literal_symbol_address
			if symbolAddress != 0:
				print(symbolAddress, ithInstruction.physical_address)
				output_file.write(str(symbolAddress) + ' \t\t\t' + str(ithInstruction.physical_address) + '\n')
			elif len(ithInstruction.error) == 0:
				print('----', '----')
				output_file.write('--- \t\t\t----- \n')
			else:
				print(ithInstruction.error)
				output_file.write(ithInstruction.error + '\n')
		output_file.write('----------------------------------------------- \n')
	# End of Main....


assembler().main()
