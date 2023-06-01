import os
import sys

def main():
    os.chdir(os.path.dirname(sys.argv[0]))

    print("##########  QUESTION 1  ###########")
    os.system("python ./question_1.py")

    print("##########  QUESTION 2  ###########")
    os.system("python ./question_2.py")

    print("##########  QUESTION 3 ###########")
    os.system("python ./question_3.py")

    print("##########  QUESTION 4 ###########")
    os.system("python ./question_4.py")



if __name__ == "__main__":
    main()
