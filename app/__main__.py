from recordScrape import RecordScraper
import sys

if __name__ == '__main__':
    detailed = False
    genre = "jazz"
    # check for command line arguments
    if len(sys.argv) > 1:
      if "detailed" in sys.argv:
        detailed = True

      if "electronic" in sys.argv:
        genre = "electronic"
      elif "rock" in sys.argv:
        genre = "rock"

    s = RecordScraper()
    s.detailed = detailed
    s.genre = genre
    s.main()