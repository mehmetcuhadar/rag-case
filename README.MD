# RAG Case Study

Bu proje kullanıcıların arXiv üzerinde yayınlanmış bilimsel makaleleri LLM sorguları ile bulabilmesini sağlayan bir sistemdir.

Sistem Retrieval Augmented Generation (RAG) mimarisi kullanarak kullanıcı sorgusuna en uygun makaleleri bulur ve LLM yardımıyla bu makaleleri kullanıcıya önerir.

Proje aşağıdaki teknolojileri kullanmaktadır:

- FastAPI (Backend API)
- React (Frontend)
- PostgreSQL (Kullanıcı ve sohbet verileri)
- Qdrant (Vector database)
- Ollama (LLM inference)

## a) Dosya Yapısı
Projede bulunan klasörler, dosyalar ve amaçları aşağıdaki gibidir:

### 1-backend:

Bu klasör FastAPI ile yazılmış API katmanını ve onun sorunsuz çalışmaya başlamasını sağlayacak ilgili dockerfile, .env, requirements.txt dosyalarını içerir.

**Backend tarafından şu işlemler yapılabilir:**

- Backend servisinin ve veritabanı bağlantılarının aktifliği kontrol edilebilir 
- Kullanıcı Kimlik Doğrulama ve Yetkilendirme işlemleri yapılabilir.
- Sohbetlerin CRUD operasyonları yapılabilir.
- Ollama servisi üzerinden LLM ile mesajlaşılabilir. Bu mesajlar da veritabanına kaydedilir.

### 2-frontend:

Bu klasör React ile yazılmış ön yüzü ve onun sorunsuz çalışmaya başlamasını sağlayacak ilgili dockerfile, .env, requirements.txt dosyalarını içerir.

**Arayüz üzerinden şu işlemler yapılabilir:**
- Kullanıcı bazlı giriş yapılabilir.
- Geçmiş sohbetler görüntülenebilir ve yeni sohbet oluşturulabilir.
- Model ile iletişim kurulabilir.
- Sohbetler yeniden adlandırılabilir veya silinebilir.

### 3-init.sql:

Bu dosya veritabanının şemasını tanımlar. Docker-compose çalıştırılırken chats, messages, refresh_tokens ve users tablolarını oluşturur.

### 4- docker-compose.yaml:

Aşağıda bulunan servisleri tanımlar ve bağımlılıklarını yönetir:

- db
- ollama
- qdrant
- backend
- frontend

db ve ollama servisi ilk ayağa kaldırılan servislerdir. Bu servisler sağlıklı bir şekilde çalıştıktan sonra backend servis çalıştırılır. backend servisi çalıştıktan sonra da en son frontend çalışır ve uygulama artık kullanıma hazırdır.

## b) Sistem Mimarisi

Proje mikroservis benzeri bir yapı ile docker-compose üzerinden çalışmaktadır.

Sistemde bulunan servisler:

- PostgreSQL → Kullanıcılar, sohbetler ve mesajlar saklanır
- Qdrant → Makalelerin embedding vektörleri saklanır
- Ollama → LLM çalıştırılır
- Backend (FastAPI) → API katmanı
- Frontend (React) → Kullanıcı arayüzü

## c) RAG Pipeline

Sistem kullanıcı sorgularını anlamak ve ilgili makaleleri bulmak için Retrieval Augmented Generation mimarisi kullanmaktadır.

Pipeline aşağıdaki şekilde çalışır:

1. Kullanıcı LLM'e frontend aracılığıyla bir soru sorar.
2. Kullanıcı sorgusu embedding model ile vektöre dönüştürülür.
3. Aynı sorgu için sparse embedding oluşturulur (BM25).
4. Qdrant üzerinde dense ve sparse vektörler kullanılarak hybrid search yapılır.
5. En alakalı makaleler bulunur. (top 5)
6. Bu makaleler LLM'e prompt olarak verilir.
7. LLM en alakalı makaleleri frontend'te kullanıcıya önerir.

## d) Kullanılan Modeller

### LLM

Ollama üzerinden çalışan model:

- gemma3:4b

Model kullanıcıya bulunan makaleleri açıklamak ve öneri sunmak için kullanılmaktadır.

### Dense Embedding Modeli

- Model: BAAI/bge-base-en-v1.5
- Boyut: 768

Bu model semantik benzerlikleri yakalamak için kullanılmaktadır.

### Sparse Embedding Modeli

- Model: BM25 (FastEmbed)

Bu model anahtar kelime eşleşmelerini yakalamak için kullanılmaktadır.

## e) Hybrid Search

Sistem makale aramalarını daha doğru yapabilmek için hybrid search kullanmaktadır.

Hybrid search iki farklı yöntemi birleştirir:

Dense Search  
Semantik benzerlikleri yakalar.

Sparse Search (BM25)  
Anahtar kelime eşleşmelerini yakalar.

Bu iki sonuç Reciprocal Rank Fusion (RRF) algoritması ile birleştirilir ve en alakalı makaleler sıralanır.

Bu yöntem özellikle teknik sorgularda daha doğru sonuçlar üretir.

## f) Projenin Çalıştırılması

Projeyi çalıştırabilmek için Docker, Docker Compose kurulu olması gerekir. Docker servisleri ayağa kaldırılmadan önce istenilerse backend klasörü altında bulunan .env dosyasından ayarlamalar yapılabilir. Hangi LLM kullanılmak isteniyorsa "MODEL_NAME" değiştirilebilir. Varsayılan olarak gemma3:4b kullanılmaktadır. İlgili model Docker servisleri ayağa kaldırıldıktan sonra eğer servisler ilk defa ayağa kaldırılıyorsa LLM'in ve örnek verisetinin indirilmesi gerekir. LLM Ollama servisinin içinde indirilmelidir. Aşağıdaki komut ile tüm servisler sırasıyla çalışacaktır:

`docker compose up --build -d `

Daha sonrasında modeli indirmek için aşağıdaki komut çalıştırılmalıdır:

`docker exec -it ollama ollama pull gemma3:4b `

Daha sonrasında ARXIV verisetini indirmek için aşağıdaki komut çalıştırılmalıdır:

`docker exec -it backend python -m app.jobs.ingest_arxiv`

Servisler başarıyla çalıştıktan ve gerekli indirmeler yapıldıktan sonra [frontend](http://localhost:8501) ve [backend](http://localhost:5000/docs)'e ulaşabilirsiniz. Backend tarafında "/health" dışındaki endpointler yetkilendirme gerektirir.
