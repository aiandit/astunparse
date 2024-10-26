flag = False

match (100, 200):

   case (100, 300):  # Mismatch: 200 != 300

       print('Case 1')

   case (100, 200) if flag:  # Successful match, but guard fails

       print('Case 2')

   case (100, y):  # Matches and binds y to 200

       print(f'Case 3, y: {y}')

   case _:  # Pattern not attempted

       print('Case 4, I match anything!')

