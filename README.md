# Blockchain_lecture

   Python Programming of Blockchain   
  
   was a series of three lectures given within the Graduate Course 
   'Blockchain and Future Society' 
   Offered in the Fall Semester 2018 at 
   GIST, Rep. of Korea. The instructor was Prof. Heung-No Lee. 
   The blockchain developed in the course was not meant to be complete. 
   Instead, aim was to understand 
   what a blockchain, and a cryptocurrency based on it, is by 
   doing a little bit of programming work. 
   
   To this end, Prof. Lee utilized the blog work 
   "Learn Blockchain by Building One" of Daniel Flymen [1],[2]. 
   Flymen's blog and his Python code offerred good introductory materials. 
   His code was also given to learn blockchain and thus was not meant to be complete. 
    
   In my course, I have given a homework assignment to improve on his work. 
   The code presented below was a result of homework assignment which 
   a group of students have worked together and made improvements. 
  
   There were several upgrades made to [2]. Just to name a few notable ones, they are 
   1) mined blocks now have "correct" block hashes with the designated leading 
   number of zeros. 2) A auto mining routine was included in which 
   the mining operation is continued at a node which listens 
   to a new block announcement and switches if a new longest chain is found. 
    
   Overall the list of functions this code can demonstrate includes: 
    1. Announcing transactions, 
    2. Including transactions into blocks, 
    3. Chaining blocks using Proof-of-Work(PoW), 
    4. Chainging the level of PoW difficulty 
        by varying the number of leading zeros in hash values, 
    5. Following the consensus rule of the longest-chain-win, and 
    6. Interworking of peer-to-peer nodes using APIs. 
   
  The source code and the relevant lecture note are available to download here in [3],[4]. 
   
    
References      :   [1] Daniel van Flymen, "Learn Blockchain by Building One," 
                        Sept. 25th, 2017, https://hackernoon.com/learn-blockchains-by-building-one-117428612f46.  
                    [2] Daniel van Flymen, Source code at https://github.com/dvf/blockchain/blob/master/blockchain.py. 
                    [3] Heung-No Lee, "Lecture Note on Python Programming of Blockchain," https://infonet.gist.ac.kr. 
                    [4] Heung-No Lee, Source Code of Python Programming of Blockchain,                                                                                                                               https://github.com/infonetGIST/Blockchain_lecture. 
